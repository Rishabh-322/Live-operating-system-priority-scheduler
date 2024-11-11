import tkinter as tk
import psutil
import threading
import time
from collections import deque, defaultdict

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority

class RoundRobinWithPriorityScheduler:
    def __init__(self, time_quantum, output_widget):
        self.priority_queues = defaultdict(deque)
        self.time = 0
        self.time_quantum = time_quantum
        self.completed_processes = []
        self.output_widget = output_widget
        self.custom_processes = []

    def add_process(self, process):
        self.priority_queues[process.priority].append(process)
        self.custom_processes.append(process)  # Track custom processes for live display
        self.update_output(f"Added custom process PID {process.pid}, Priority {process.priority}")

    def execute(self):
        for priority_level in sorted(self.priority_queues.keys()):
            queue = self.priority_queues[priority_level]
            self.update_output(f"\n-- Running custom processes in priority level {priority_level} --")
            while queue:
                current_process = queue.popleft()
                time_slice = min(self.time_quantum, current_process.remaining_time)
                current_process.remaining_time -= time_slice
                self.time += time_slice

                self.update_output(f"Running PID {current_process.pid}, time slice {time_slice}, remaining {current_process.remaining_time}")

                if current_process.remaining_time == 0:
                    self.update_output(f"Completed PID {current_process.pid}")
                    self.completed_processes.append(current_process)
                else:
                    queue.append(current_process)

            if not queue:
                del self.priority_queues[priority_level]

    def update_output(self, message):
        self.output_widget.insert(tk.END, message + "\n")
        self.output_widget.see(tk.END)

class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Scheduler with Live System Monitoring")

        # GUI elements
        tk.Label(root, text="Process ID").grid(row=0, column=0)
        tk.Label(root, text="Arrival Time").grid(row=1, column=0)
        tk.Label(root, text="Burst Time").grid(row=2, column=0)
        tk.Label(root, text="Priority").grid(row=3, column=0)
        tk.Label(root, text="Time Quantum").grid(row=4, column=0)

        self.pid_entry = tk.Entry(root)
        self.arrival_entry = tk.Entry(root)
        self.burst_entry = tk.Entry(root)
        self.priority_entry = tk.Entry(root)
        self.quantum_entry = tk.Entry(root)

        self.pid_entry.grid(row=0, column=1)
        self.arrival_entry.grid(row=1, column=1)
        self.burst_entry.grid(row=2, column=1)
        self.priority_entry.grid(row=3, column=1)
        self.quantum_entry.grid(row=4, column=1)

        self.output_box = tk.Text(root, height=15, width=60)
        self.output_box.grid(row=0, column=3, rowspan=6, padx=10)
        self.system_output_box = tk.Text(root, height=15, width=60)
        self.system_output_box.grid(row=8, column=0, columnspan=4, padx=10)

        tk.Button(root, text="Set Time Quantum", command=self.set_time_quantum).grid(row=5, column=0)
        tk.Button(root, text="Add Custom Process", command=self.add_custom_process).grid(row=5, column=1)
        tk.Button(root, text="Run Scheduler", command=self.run_scheduler).grid(row=6, column=0, columnspan=2)

        self.scheduler = None
        self.monitoring_thread = threading.Thread(target=self.monitor_system_processes)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def set_time_quantum(self):
        try:
            time_quantum = int(self.quantum_entry.get())
            self.scheduler = RoundRobinWithPriorityScheduler(time_quantum, self.output_box)
            self.output_box.insert(tk.END, f"Time Quantum set to {time_quantum}\n")
        except ValueError:
            tk.messagebox.showerror("Input Error", "Enter a valid integer for Time Quantum.")

    def add_custom_process(self):
        try:
            pid = int(self.pid_entry.get())
            arrival_time = int(self.arrival_entry.get())
            burst_time = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())

            if not self.scheduler:
                tk.messagebox.showerror("Scheduler Error", "Set the time quantum first.")
                return

            process = Process(pid, arrival_time, burst_time, priority)
            self.scheduler.add_process(process)
        except ValueError:
            tk.messagebox.showerror("Input Error", "Enter valid integers for all fields.")

    def run_scheduler(self):
        if self.scheduler:
            self.scheduler.execute()
        else:
            tk.messagebox.showerror("Scheduler Error", "Set the time quantum first.")

    def monitor_system_processes(self):
        """Continuously update the live memory usage and task list, including custom processes."""
        while True:
            self.system_output_box.delete(1.0, tk.END)  # Clear previous entries

            # Display live system processes
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    pid = proc.info['pid']
                    name = proc.info['name']
                    memory = proc.info['memory_info'].rss // (1024 * 1024)  # Convert to MB
                    self.system_output_box.insert(tk.END, f"PID {pid}: {name} - Memory: {memory}MB\n")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            # Display custom processes
            if self.scheduler:
                self.system_output_box.insert(tk.END, "\n--- Custom Processes ---\n")
                for process in self.scheduler.custom_processes:
                    status = "Completed" if process in self.scheduler.completed_processes else "Running"
                    remaining_time = process.remaining_time if process.remaining_time > 0 else 0
                    self.system_output_box.insert(
                        tk.END,
                        f"Custom PID {process.pid}: Priority {process.priority} - Remaining: {remaining_time} - Status: {status}\n"
                    )

            # Ensure the text box scrolls to the latest content
            self.system_output_box.see(tk.END)
            
            # Slow down the loop to make the output readable
            time.sleep(5)  # Update every 5 seconds
            
# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()

