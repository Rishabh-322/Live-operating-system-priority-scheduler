import tkinter as tk
from tkinter import messagebox
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

    def add_process(self, process):
        self.priority_queues[process.priority].append(process)
        self.update_output(f"Process {process.pid} with priority {process.priority} added to queue.")

    def execute(self):
        for priority_level in sorted(self.priority_queues.keys()):
            queue = self.priority_queues[priority_level]
            self.update_output(f"\n-- Executing processes in priority level {priority_level} --")
            while queue:
                current_process = queue.popleft()
                time_slice = min(self.time_quantum, current_process.remaining_time)
                current_process.remaining_time -= time_slice
                self.time += time_slice

                self.update_output(f"Process {current_process.pid} is running at time {self.time}, {current_process.remaining_time} remaining.")

                if current_process.remaining_time == 0:
                    self.update_output(f"Process {current_process.pid} completed at time {self.time}.")
                    self.completed_processes.append(current_process)
                else:
                    self.update_output(f"Process {current_process.pid} will continue later, returning to queue.")
                    queue.append(current_process)

            if not queue:
                del self.priority_queues[priority_level]

    def show_completed(self):
        self.update_output("\nCompleted Processes:")
        for process in self.completed_processes:
            self.update_output(f"Process {process.pid} - Priority: {process.priority}, Completed at time {self.time - process.burst_time}")

    def update_output(self, message):
        """Helper function to update output widget."""
        self.output_widget.insert(tk.END, message + "\n")
        self.output_widget.see(tk.END)


class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Round Robin with Priority Queue Scheduler")

        # GUI Elements
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

        self.output_box = tk.Text(root, height=15, width=50)
        self.output_box.grid(row=0, column=3, rowspan=6, padx=10)

        # Buttons
        tk.Button(root, text="Set Time Quantum", command=self.set_time_quantum).grid(row=5, column=0)
        tk.Button(root, text="Add Process", command=self.add_process).grid(row=5, column=1)
        tk.Button(root, text="Execute Scheduler", command=self.execute_scheduler).grid(row=6, column=0, columnspan=2)
        tk.Button(root, text="Show Completed Processes", command=self.show_completed).grid(row=7, column=0, columnspan=2)

        self.scheduler = None

    def set_time_quantum(self):
        try:
            time_quantum = int(self.quantum_entry.get())
            self.scheduler = RoundRobinWithPriorityScheduler(time_quantum, self.output_box)
            self.output_box.insert(tk.END, f"Time Quantum set to {time_quantum}\n")
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid integer for time quantum.")

    def add_process(self):
        try:
            pid = int(self.pid_entry.get())
            arrival_time = int(self.arrival_entry.get())
            burst_time = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())

            if not self.scheduler:
                messagebox.showerror("Scheduler Error", "Please set the time quantum first.")
                return

            process = Process(pid, arrival_time, burst_time, priority)
            self.scheduler.add_process(process)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for all fields.")

    def execute_scheduler(self):
        if self.scheduler:
            self.scheduler.execute()
        else:
            messagebox.showerror("Scheduler Error", "Please set the time quantum first.")

    def show_completed(self):
        if self.scheduler:
            self.scheduler.show_completed()
        else:
            messagebox.showerror("Scheduler Error", "Please set the time quantum first.")


# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerGUI(root)
    root.mainloop()
