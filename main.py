import csv
import datetime
from tkinter import *
from tkinter import ttk

# ===================================================
# 定数
# ===================================================
CLEANER_HEADER = ["id", "name", "exc", "def", "prev", "mc", "vc", "md", "vd"]
CLEANER_PATH = "./files/Cleaner.csv"
HISTORY_HEADER = ["date", "m1", "m2", "v1", "v2", "v3"]
HISTORY_PATH = "./files/History.csv"

MOP_NUM = 2
VACUUM_NUM = 3

CLEANING_WEEK_DAY = 3

# ===================================================
#  関数
# ===================================================
# ファイル操作
def Read(path, header):
    data = []
    with open(path, "r", encoding="utf-8", newline='') as file:
        for row in  csv.DictReader(file, header):
            data.append(row)
    return data[1:]

def Write(path, header, data):
     with open(path, "w", encoding="utf-8", newline='') as file:
        writer = csv.DictWriter(file, header)
        writer.writeheader()
        writer.writerows(data)

# 抽選
def Lottery(l_date, l_charge):
    cleaner_data = Read(CLEANER_PATH, CLEANER_HEADER)
    sorted_data = sorted(cleaner_data, key=lambda x: x["prev"])
    pick_data = sorted_data[:(MOP_NUM + VACUUM_NUM)]
    pick_sorted_data = sorted(pick_data, key=lambda x: x["md"])

    result = {"mop" : pick_sorted_data[:MOP_NUM], "vacuum" : pick_sorted_data[MOP_NUM:]}
    print("[モップ] %s | %s" % (result["mop"][0]["name"], result["mop"][1]["name"]))
    print("[掃除機] %s | %s | %s" % (result["vacuum"][0]["name"], result["vacuum"][1]["name"], result["vacuum"][2]["name"]))

    next_day = GetNextCleaningDay()
    history_data = Read(HISTORY_PATH, HISTORY_HEADER)

    if history_data and history_data[-1]["date"] == next_day:
            history_data.pop(-1)

    history_data.append({"date" : next_day, "m1" : result["mop"][0]["id"], "m2" : result["mop"][1]["id"], "v1" : result["vacuum"][0]["id"], "v2" : result["vacuum"][1]["id"], "v3" : result["vacuum"][2]["id"]})
    Write(HISTORY_PATH, HISTORY_HEADER, history_data)

    UpdateOutput(l_date, l_charge)

# 日付操作
def GetNextCleaningDay():
    date = datetime.date.today()
    while date.weekday() != CLEANING_WEEK_DAY:
        date += datetime.timedelta(1)
    
    return date.strftime("%Y/%m/%d")

# リセット
def ResetCleanerData():
    cleaner_data = Read(CLEANER_PATH, CLEANER_HEADER)

    for data in cleaner_data:
        data["exc"] = data["def"]

    Write(CLEANER_PATH, CLEANER_HEADER, cleaner_data)

# 決定
def ConfirmCharge():
    cleaner_data = Read(CLEANER_PATH, CLEANER_HEADER)
    history_data = Read(HISTORY_PATH, HISTORY_HEADER)
    if not history_data:
        print("[ERROR] History Data is empty.")
        return

    date = history_data[-1]["date"]
    mop_id = [history_data[-1]["m1"], history_data[-1]["m2"]]
    for id in mop_id:
        for data in cleaner_data:
            if id == data["id"] and date != data["md"]:
                data["mc"] = int(data["mc"]) + 1
                data["md"] = date
    
    vac_id = [history_data[-1]["v1"], history_data[-1]["v2"], history_data[-1]["v3"]]
    for id in vac_id:
        for data in cleaner_data:
            if id == data["id"] and date != data["vd"]:
                data["vc"] = int(data["vc"]) + 1
                data["vd"] = date

    Write(CLEANER_PATH, CLEANER_HEADER, cleaner_data)

# 出力更新
def UpdateOutput(l_date, l_charge):
    cleaner_data = Read(CLEANER_PATH, CLEANER_HEADER)
    history_data = Read(HISTORY_PATH, HISTORY_HEADER)
    if history_data and history_data[-1]['date'] == GetNextCleaningDay():
        date_str = "NEXT: %s" % (history_data[-1]['date'])
        name = GetCleanerName([history_data[-1]['m1'], history_data[-1]['m2'], history_data[-1]['v1'], history_data[-1]['v2'], history_data[-1]['v3']])
        charge_str = "[MOP] %s | %s\n[VACUUM] %s | %s | %s" % (name[0], name[1], name[2], name[3], name[4])
        l_date["text"] = date_str
        l_charge["text"] = charge_str
    else:
        date_str = "NEXT: %s" % (GetNextCleaningDay())
        charge_str = "-- HAVEN'T BEEN LOTTERY YET --"
        l_date["text"] = date_str
        l_charge["text"] = charge_str

def GetCleanerName(ids):
    cleaner_data = Read(CLEANER_PATH, CLEANER_HEADER)
    retval = []

    for id in ids:
        for data in cleaner_data:
            if id == data["id"]:
                retval.append(data["name"])
    
    return retval

# ===================================================
# main
# ===================================================
if __name__ == "__main__":
    root = Tk()
    root.title("CleanerManager")
    root.grid()

    f_top = ttk.Frame(root, padding=20, relief="groove")
    f_top.grid(row=0, column=0)

    l_date = ttk.Label(f_top, text="NEXT: 2023/08/12", font=("Helvetica", 12, "bold"))
    l_date.grid(row=0, column=0)
    l_charge = ttk.Label(f_top, justify="left", font=("Helvetica", 12), text="[MOP] AAA | BBB\n[VACUUM] CCC | DDD | EEE")
    l_charge.grid(row=1, column=0)

    f_bottom = ttk.Frame(root, padding=20)
    f_bottom.grid(row=1, column=0)

    b_reset = ttk.Button(f_bottom, text="RESET", command=ResetCleanerData())
    b_reset.grid(row=0, column=0)
    b_confirm = ttk.Button(f_bottom, text="CONFIRM", command=ConfirmCharge())
    b_confirm.grid(row=0, column=1)
    b_lottery = ttk.Button(f_bottom, text="LOTTERY", command=Lottery(l_date, l_charge))
    b_lottery.grid(row=1, column=0)

    UpdateOutput(l_date, l_charge)

    root.mainloop()
