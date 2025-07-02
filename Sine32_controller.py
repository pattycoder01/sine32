import mido
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time

transpose_amount = 0  # transposition

class MidiPatchbaySerial:
    def __init__(self, master):
        self.master = master
        self.master.title("Sine32 Controller")

        self.running = False
        self.inport = None
        self.ser = None
        self.thread = None

        self.transposition_var = tk.IntVar(value=transpose_amount)

        ttk.Label(master, text="MIDI Input Port:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.in_combo = ttk.Combobox(master, state="readonly", width=40)
        self.in_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(master, text="Serial Port:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.serial_combo = ttk.Combobox(master, state="readonly", width=40)
        self.serial_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.baud_label = ttk.Label(master, text="Baudrate:")
        self.baud_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.baud_entry = ttk.Entry(master)
        self.baud_entry.insert(0, "115200")
        self.baud_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(master, text="Transposition:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.transposition_spin = tk.Spinbox(master, from_=-24, to=24, textvariable=self.transposition_var, width=5)
        self.transposition_spin.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        control_frame = ttk.LabelFrame(root, text="Controls", padding=10)
        control_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start)
        self.start_button.grid(row=4, column=0, padx=5, pady=10)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop, state="disabled")
        self.stop_button.grid(row=4, column=1, padx=5, pady=10)

        self.refresh_button = ttk.Button(control_frame, text="Refresh", command=self.refresh_ports)
        self.refresh_button.grid(row=4, column=2, pady=5)

        self.log_text = tk.Text(master, height=10, width=60, state="disabled")
        self.log_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        self.refresh_ports()

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def refresh_ports(self):
        self.in_ports = mido.get_input_names()
        self.serial_ports = self.get_serial_ports()

        self.in_combo['values'] = self.in_ports
        self.serial_combo['values'] = self.serial_ports

        if self.in_combo.get() not in self.in_ports:
            self.in_combo.set('')
        if self.serial_combo.get() not in self.serial_ports:
            self.serial_combo.set('')

        self.log("Ports refreshed")

    def get_serial_ports(self):
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]

    def start(self):
        if self.running:
            return

        in_port_name = self.in_combo.get()
        serial_port_name = self.serial_combo.get()
        baud = int(self.baud_entry.get())

        if not in_port_name or not serial_port_name:
            messagebox.showerror("Error", "Please select a MIDI port as well as a serial port!")
            return

        try:
            self.inport = mido.open_input(in_port_name)
            self.ser = serial.Serial(serial_port_name, baud, timeout=0.1)
            time.sleep(2)  # Warten, bis Arduino bereit ist
        except Exception as e:
            messagebox.showerror("Error", f"Opening ports failed:\n{e}")
            self.log(f"[ERROR] {e}")
            return

        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        self.thread = threading.Thread(target=self.route_midi, daemon=True)
        self.thread.start()
        self.log("Started routing")

    def route_midi(self):
        while self.running:
            for msg in self.inport.iter_pending():
                if msg.type in ['note_on', 'note_off']:
                    note = max(0, min(127, msg.note + transpose_amount))
                    velocity = msg.velocity if msg.type == 'note_on' else 0
                    on_off = 1 if velocity > 0 else 0
                    send_str = f"[{note};{velocity};{on_off}]\n"
                    try:
                        self.ser.write(send_str.encode('ascii'))
                        self.log(f"Sent: {send_str.strip()}")
                    except Exception as e:
                        self.log(f"[ERROR] Serial write failed: {e}")
            time.sleep(0.001)

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self.inport:
            self.inport.close()
            self.inport = None
        if self.ser:
            self.ser.close()
            self.ser = None
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log("Stopped routing")

if __name__ == "__main__":
    root = tk.Tk()
    app = MidiPatchbaySerial(root)
    root.mainloop()
