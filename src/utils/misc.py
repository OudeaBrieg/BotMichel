from prettytable import PrettyTable
import os
import shutil
import psutil

def count_parameters(model): 
    table = PrettyTable(["Modules", "Parameters"]) 
    total_params = 0 
    for name, parameter in model.get_parameters(): 
        if not parameter.requires_grad: 
            continue 
        params = parameter.numel() 
        table.add_row([name, params]) 
        total_params += params 
    print(table)
    print(f"Total Trainable Params: {total_params}") 
    return total_params

def clear_folder(path):
    print(f"Clearing all files in {path}")
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    print(f"Cleared {path}")

def estimate_supported_processes():
    mem_instance_launch = 3.5e9
    vm = psutil.virtual_memory()
    # Need 3.5GB to launch, reduces to 350MB after a while
    est_proc_mem = round(
        (vm.available - mem_instance_launch)
        / mem_instance_launch
    )
    est_proc_cpu = os.cpu_count()
    est_proc = min(est_proc_mem, est_proc_cpu)
    return est_proc