from gui.app_ui import LicensePlateApp


def main():
    print("   HỆ THỐNG NHẬN DIỆN BIỂN SỐ XE - AI   ")

    try:
        app = LicensePlateApp()
        app.mainloop()
        
    except Exception as e:
        print(f"Ứng dụng gặp lỗi nghiêm trọng: {e}")
        input("Bấm Enter để thoát...")

if __name__ == "__main__":
    main()