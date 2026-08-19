import flet as ft
import sqlite3
import os
import shutil
import uuid
import hashlib
from datetime import datetime
#########
print("RUNNING FILE:", __file__)
subject_images = []
file_picker = None

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "database",
    "database.db"
)


IMAGE_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMAGE_DIR, exist_ok=True)
#############

def ensure_transfer_id():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    # ساخت ستون در دیتابیس‌های قدیمی
    cursor.execute(
        "PRAGMA table_info(records)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "transfer_id" not in columns:

        cursor.execute(
            "ALTER TABLE records "
            "ADD COLUMN transfer_id TEXT"
        )

    # رکوردهای قدیمی که transfer_id ندارند
    cursor.execute("""
        SELECT id
        FROM records
        WHERE transfer_id IS NULL
           OR transfer_id = ''
    """)

    rows = cursor.fetchall()

    for row in rows:

        transfer_id = str(
            uuid.uuid4()
        )

        cursor.execute("""
            UPDATE records
            SET transfer_id = ?
            WHERE id = ?
        """, (
            transfer_id,
            row[0]
        ))

    connection.commit()
    connection.close()

    ensure_transfer_id()

    print(
        "TRANSFER ID CHECK COMPLETED:",
        len(rows),
        "OLD RECORDS UPDATED"
    )


COLUMNS = [
    "تاریخ اعلام موضوع",
    "شرح موضوع",
    "اشخاص مرتبط",
    "سوابق",
    "تاریخ انجام-پیگیری",
    "وضعیت",
    "محول به",
    "تاریخ",
    "توضیحات",
]


def load_records():

    if not os.path.exists(DATABASE_PATH):
        return []

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            date1,
            subject,
            subject_images,
            people,
            history,
            history_images,
            follow_date,
            status,
            assigned,
            date2,
            description,
            description_images
            transfer_id
        FROM records
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    connection.close()

    return records

######################
def main(page):

    page.title = "AssetManager"

    page.bgcolor = ft.Colors.WHITE


    # -----------------------------
    # ادامه کد اصلی برنامه
    # -----------------------------
    
    file_picker = ft.FilePicker()

    page.services.append(file_picker)

    

    print("FILE PICKER CONNECTED")
    page.title = "AssetManager"

    page.rtl = True

    page.scroll = ft.ScrollMode.AUTO

    page.padding = 15

    page.scroll = ft.ScrollMode.AUTO

    page.theme_mode = ft.ThemeMode.LIGHT

    title = ft.Text(
        "مدیریت اطلاعات",
        size=24,
        weight=ft.FontWeight.BOLD,
    )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "تاریخ اعلام موضوع",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=130,
                )
            ),

            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "شرح موضوع",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=220,
                )
            ),

            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "اشخاص مرتبط",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=150,
                )
            ),

            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "سوابق",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=220,
                )
            ),

            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "تاریخ انجام-پیگیری",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=150,
                )
            ),

            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "وضعیت",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=120,
                )
            ),

            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "محول به",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=130,
                )
            ),

            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "تاریخ",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=120,
                )
            ),

            ft.DataColumn(
                ft.Container(
                    content=ft.Text(
                        "توضیحات",
                        weight=ft.FontWeight.BOLD,
                        no_wrap=True,
                    ),
                    width=220,
                )
            ),
        ],
        rows=[],

        border=ft.Border.all(1),

        column_spacing=5,

        horizontal_lines=ft.BorderSide(1),
        vertical_lines=ft.BorderSide(1),

        heading_row_height=45,
        data_row_min_height=35,
        data_row_max_height=55,

        expand=True,
        horizontal_margin=10,
        divider_thickness=1,
    )
    TABLE_WIDTH = 1500

    custom_table = ft.ListView(
        width=TABLE_WIDTH,
        expand=True,
        spacing=0,
        auto_scroll=False,
    )
    search_text = ""
    #################################
    def create_table_header():

        widths = [
            130,   # تاریخ اعلام موضوع
            240,   # شرح موضوع
            140,   # اشخاص مرتبط
            240,   # سوابق
            140,   # تاریخ پیگیری
            120,   # وضعیت
            140,   # محول به
            110,   # تاریخ
            240,   # توضیحات
        ]

        headers = []

        for i, column in enumerate(COLUMNS):

            headers.append(
                ft.Container(

                    width=widths[i],
                    height=58,

                    bgcolor=ft.Colors.BLUE_GREY_800,

                    content=ft.Text(
                        column,

                        size=13,

                        weight=ft.FontWeight.BOLD,

                        color=ft.Colors.WHITE,

                        text_align=ft.TextAlign.CENTER,

                        max_lines=2,

                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),

                    alignment=ft.Alignment.CENTER,

                    padding=ft.Padding.symmetric(
                        horizontal=8,
                        vertical=6,
                    ),

                    border=ft.Border(
                        right=ft.BorderSide(
                            0.5,
                            ft.Colors.BLUE_GREY_600,
                        ),
                        bottom=ft.BorderSide(
                            1,
                            ft.Colors.BLUE_GREY_900,
                        ),
                    ),
                )
            )

        return ft.Container(

            width=sum(widths),

            bgcolor=ft.Colors.BLUE_GREY_800,

            border_radius=ft.BorderRadius.only(
                top_left=8,
                top_right=8,
            ),

                content=ft.Row(
                controls=headers,
                spacing=0,
                wrap=False,
                tight=True,
            ),
        )

    def create_table_row(record):
        print("CREATE TABLE ROW CALLED")

        widths = [
            130,   # تاریخ اعلام موضوع
            240,   # شرح موضوع
            140,   # اشخاص مرتبط
            240,   # سوابق
            140,   # تاریخ انجام-پیگیری
            120,   # وضعیت
            140,   # محول به تاریخ
            110,   # تاریخ دوم
            240,   # توضیحات
        ]

        values = [
            record[1],
            record[2],
            record[4],
            record[5],
            record[7],
            record[8],
            record[9],
            record[10],
            record[11],
        ]

        cells = []

        for index, value in enumerate(values):

            text_value = (
                ""
                if value is None
                else str(value)
            )

            # ------------------------------------------
            # وضعیت
            # ------------------------------------------

            if index == 5:

                status_text = text_value

                if status_text == "انجام شد":
                    status_bg = ft.Colors.GREEN_50
                    status_color = ft.Colors.GREEN_800

                elif status_text == "در حال انجام":
                    status_bg = ft.Colors.ORANGE_50
                    status_color = ft.Colors.ORANGE_800

                elif status_text == "در حال بررسی":
                    status_bg = ft.Colors.BLUE_50
                    status_color = ft.Colors.BLUE_800

                elif status_text == "مختومه":
                    status_bg = ft.Colors.GREY_200
                    status_color = ft.Colors.GREY_800

                else:
                    status_bg = ft.Colors.GREY_50
                    status_color = ft.Colors.GREY_700

                cell_content = ft.Container(
                    content=ft.Text(
                        status_text,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=status_color,
                        text_align=ft.TextAlign.CENTER,
                    ),

                    bgcolor=status_bg,

                    padding=ft.Padding.symmetric(
                        horizontal=10,
                        vertical=6,
                    ),

                    border_radius=20,

                    alignment=ft.Alignment.CENTER,
                )

                cell = ft.Container(
                    width=widths[index],
                    height=58,

                    content=cell_content,

                    alignment=ft.Alignment.CENTER,

                    padding=ft.Padding.symmetric(
                        horizontal=8,
                        vertical=6,
                    ),

                    border=ft.Border(
                        right=ft.BorderSide(
                            0.5,
                            ft.Colors.GREY_300,
                        ),
                        bottom=ft.BorderSide(
                            0.5,
                            ft.Colors.GREY_300,
                        ),
                    ),
                )

            else:

                cell = ft.Container(
                    width=widths[index],
                    height=64,

                    content=ft.Text(
                        text_value,
                        size=13,

                        color=ft.Colors.GREY_800,

                        max_lines=2,

                        overflow=ft.TextOverflow.ELLIPSIS,

                        no_wrap=False,

                        text_align=ft.TextAlign.RIGHT,
                    ),

                    alignment=ft.Alignment.CENTER_RIGHT,

                    padding=ft.Padding.symmetric(
                        horizontal=12,
                        vertical=6,
                    ),

                    bgcolor=(
                        ft.Colors.WHITE
                        if index % 2 == 0
                        else ft.Colors.GREY_50
                    ),

                    border=ft.Border(
                        right=ft.BorderSide(
                            0.5,
                            ft.Colors.GREY_300,
                        ),
                        bottom=ft.BorderSide(
                            0.5,
                            ft.Colors.GREY_300,
                        ),
                    ),
                )

            cells.append(cell)

        row_width = sum(widths)

        print(
            "ROW WIDTH:",
            row_width
        )

        return ft.Container(
            width=row_width,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,

            margin=ft.Margin.symmetric(
                vertical=3,
                horizontal=2,
            ),

            padding=0,

            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=3,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 1),
            ),

            ink=True,

            on_click=lambda e: edit_record(record[0]),

            content=ft.Row(
                controls=cells,
                spacing=0,
                tight=True,
            ),
        )
    
    ################################
    def delete_record(record_id):

        connection = sqlite3.connect(DATABASE_PATH)

        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM records WHERE id = ?",
            (record_id,)
        )

        connection.commit()

        connection.close()

        refresh_table()
        page.update()

    #delete_button = ft.ElevatedButton(
       # "حذف رکورد",
       # on_click=lambda e: delete_record(record[0])
    #)


    def edit_record(record_id):

        connection = sqlite3.connect(DATABASE_PATH)

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                date1,
                subject,
                subject_images,
                people,
                history,
                history_images,
                follow_date,
                status,
                assigned,
                date2,
                description,
                description_images
            FROM records
            WHERE id = ?
        """, (record_id,))

        record = cursor.fetchone()
        print("EDIT RECORD DATA:", record)

        connection.close()

        if record is None:
            return

        open_edit_dialog(record)
    ##############تابع نمایش عکس
    def show_images(images, record_id=None, image_column=None):

        if not images:
            print("NO IMAGES")
            return

        if isinstance(images, str):
            image_list = images.split("|")
        else:
            image_list = list(images)

        image_list = [
            img for img in image_list
            if img
        ]

        if not image_list:
            print("NO VALID IMAGES")
            return

        print("IMAGE LIST:", image_list)
        print("RECORD ID:", record_id)
        print("IMAGE COLUMN:", image_column)

        current_index = 0

        image_view = ft.Image(
            src="",
            width=min(page.width * 0.85, 700),
            height=min(page.height * 0.55, 450),
            fit="contain",
        )

        counter = ft.Text(
            "",
            text_align=ft.TextAlign.CENTER,
        )

        def load_image():

            if not image_list:
                return

            full_path = os.path.join(
                BASE_DIR,
                image_list[current_index]
            )

            print(
                "SHOW IMAGE:",
                current_index + 1,
                "OF",
                len(image_list),
                full_path
            )

            if not os.path.exists(full_path):
                print(
                    "IMAGE NOT FOUND:",
                    full_path
                )
                return

            image_view.src = full_path

            counter.value = (
                f"{current_index + 1} از "
                f"{len(image_list)}"
            )

            previous_button.disabled = (
                current_index == 0
            )

            next_button.disabled = (
                current_index == len(image_list) - 1
            )

            delete_button.disabled = (
                record_id is None
                or image_column is None
            )

            page.update()

        def next_image(e):

            nonlocal current_index

            print("NEXT BUTTON CLICKED")

            if current_index < len(image_list) - 1:

                current_index += 1

                print(
                    "NEW INDEX:",
                    current_index
                )

                load_image()

        def previous_image(e):

            nonlocal current_index

            print("PREVIOUS BUTTON CLICKED")

            if current_index > 0:

                current_index -= 1

                print(
                    "NEW INDEX:",
                    current_index
                )

                load_image()

        def delete_current_image(e):

            nonlocal current_index

            if not image_list:
                return

            if record_id is None or image_column is None:
                print("DELETE IMAGE ERROR: RECORD/COLUMN NOT PROVIDED")
                return

            image_path = image_list[current_index]

            full_path = os.path.join(
                BASE_DIR,
                image_path
            )

            print("DELETE IMAGE:", full_path)

            # حذف فایل از پوشه
            if os.path.exists(full_path):

                try:
                    os.remove(full_path)

                    print(
                        "IMAGE FILE DELETED:",
                        full_path
                    )

                except Exception as ex:

                    print(
                        "IMAGE FILE DELETE ERROR:",
                        ex
                    )

                    return

            # حذف مسیر عکس از لیست
            image_list.pop(current_index)

            # به‌روزرسانی دیتابیس
            connection = sqlite3.connect(
                DATABASE_PATH
            )

            cursor = connection.cursor()

            new_images = "|".join(image_list)

            cursor.execute(
                f"""
                UPDATE records
                SET {image_column} = ?
                WHERE id = ?
                """,
                (
                    new_images,
                    record_id
                )
            )

            connection.commit()
            connection.close()

            print(
                "DATABASE IMAGE PATHS UPDATED:",
                new_images
            )

            # اگر دیگر عکسی باقی نمانده
            if not image_list:

                image_dialog.open = False

                refresh_table()

                page.update()

                print("ALL IMAGES DELETED")

                return

            # اگر آخرین عکس حذف شده بود
            if current_index >= len(image_list):

                current_index = len(image_list) - 1

            load_image()

            refresh_table()

            page.update()

        def close_image(e):

            print(
                "CLOSE IMAGE BUTTON CLICKED"
            )

            image_dialog.open = False

            page.update()

        previous_button = ft.TextButton(
            "◀ قبلی",
            on_click=previous_image,
        )

        next_button = ft.TextButton(
            "بعدی ▶",
            on_click=next_image,
        )

        delete_button = ft.TextButton(
            "🗑 حذف عکس",
            on_click=delete_current_image,
        )

        close_button = ft.TextButton(
            "بستن",
            on_click=close_image,
        )

        image_dialog = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "نمایش تصاویر",
                size=18,
            ),

            content=ft.Container(
                content=ft.Column(
                    [
                        image_view,
                        counter,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                width=min(page.width * 0.9, 750),
                height=min(page.height * 0.7, 520),
                padding=5,
            ),

            actions=[
                previous_button,
                next_button,
                delete_button,
                close_button,
            ],

            actions_alignment=ft.MainAxisAlignment.CENTER,
        )

        page.overlay.append(
            image_dialog
        )

        image_dialog.open = True

        load_image()


        page.update()

############################
    def open_edit_dialog(record):

        subject_images = (
            (record[3] or "").split("|")
            if record[3]
            else []
        )

        history_images = (
            (record[6] or "").split("|")
            if record[6]
            else []
        )

        description_images = (
            (record[12] or "").split("|")
            if record[12]
            else []
        )
        ################################
        date1 = ft.TextField(
            label="تاریخ اعلام موضوع",
            value=record[1] or ""
        )
        
        subject_image_button = ft.ElevatedButton(
            "نمایش عکس‌های شرح موضوع",
            on_click=lambda e: show_images(
                subject_images.copy(),
                record[0],
                "subject_images"
            )
        )

        subject = ft.TextField(
            label="شرح موضوع",
            value=record[2] or "",
            multiline=True,
            min_lines=3,
            max_lines=6,
        )

        people = ft.TextField(
            label="اشخاص مرتبط",
            value=record[4] or ""
        )

        history = ft.TextField(
            label="سوابق",
            value=record[5] or "",
            multiline=True,
            min_lines=3,
            max_lines=6,
        )

        history_image_button = ft.ElevatedButton(
            "نمایش عکس‌های سوابق",
            on_click=lambda e: show_images(
                history_images.copy(),
                record[0],
                "history_images"
            )
        )

        follow_date = ft.TextField(
            label="تاریخ انجام-پیگیری",
            value=record[7] or ""
        )

        status = ft.Dropdown(
            label="وضعیت",
            value=record[8] or "",
            options=[
                ft.DropdownOption("در حال بررسی"),
                ft.DropdownOption("در حال انجام"),
                ft.DropdownOption("انجام شد"),
                ft.DropdownOption("مختومه"),
            ],
        )

        assigned = ft.TextField(
            label="محول به",
            value=record[9] or ""
        )

        date2 = ft.TextField(
            label="تاریخ",
            value=record[10] or ""
        )

        description = ft.TextField(
            label="توضیحات",
            value=record[11] or "",
            multiline=True,
            min_lines=3,
            max_lines=6,
        )
        ####################
        async def add_edit_subject_image(e):

            files = await file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=[
                    "png",
                    "jpg",
                    "jpeg"
                ]
            )

            if not files:
                return

            for file in files:

                import uuid

                filename = (
                    str(uuid.uuid4())
                    + "_"
                    + os.path.basename(file.path)
                )

                destination = os.path.join(
                    IMAGE_DIR,
                    filename
                )

                shutil.copy2(
                    file.path,
                    destination
                )

                subject_images.append(
                    os.path.join(
                        "images",
                        filename
                    )
                )
                print("CURRENT SUBJECT IMAGES:", subject_images)
                print("EDIT SUBJECT SAVED:", destination)

        async def add_edit_history_image(e):

            files = await file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=[
                    "png",
                    "jpg",
                    "jpeg"
                ]
            )

            if not files:
                return

            for file in files:

                import uuid

                filename = (
                    str(uuid.uuid4())
                    + "_"
                    + os.path.basename(file.path)
                )

                destination = os.path.join(
                    IMAGE_DIR,
                    filename
                )

                shutil.copy2(
                    file.path,
                    destination
                )

                history_images.append(
                    os.path.join(
                        "images",
                        filename
                    )
                )
                print("CURRENT HISTORY IMAGES:", history_images)
                print("EDIT HISTORY SAVED:", destination)

        async def add_edit_description_image(e):

            files = await file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=[
                    "png",
                    "jpg",
                    "jpeg"
                ]
            )

            if not files:
                return

            for file in files:

                import uuid

                filename = (
                    str(uuid.uuid4())
                    + "_"
                    + os.path.basename(file.path)
                )

                destination = os.path.join(
                    IMAGE_DIR,
                    filename
                )

                shutil.copy2(
                    file.path,
                    destination
                )

                description_images.append(
                    os.path.join(
                        "images",
                        filename
                    )
                )
                print("CURRENT DESCRIPTION IMAGES:", description_images)
                print("EDIT DESCRIPTION SAVED:", destination)

        ######################
        description_image_button = ft.ElevatedButton(
            "نمایش عکس‌های توضیحات",
            on_click=lambda e: show_images(
                description_images.copy(),
                record[0],
                "description_images"
            )
        )
        ###############################
        edit_subject_image_button = ft.ElevatedButton(
            "افزودن عکس شرح موضوع",
            on_click=add_edit_subject_image
        )


        edit_history_image_button = ft.ElevatedButton(
            "افزودن عکس سوابق",
            on_click=add_edit_history_image
        )


        edit_description_image_button = ft.ElevatedButton(
            "افزودن عکس توضیحات",
            on_click=add_edit_description_image
        )
        delete_button = ft.ElevatedButton(
            "حذف رکورد",
            on_click=lambda e: delete_record(record[0])
)
        ############################
        dialog = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "ویرایش اطلاعات",
                size=20,
            ),

            content=ft.Container(
                content=ft.Column(
                    [
                        date1,

                        subject,
                        edit_subject_image_button,
                        subject_image_button,

                        people,

                        history,
                        edit_history_image_button,
                        history_image_button,

                        follow_date,
                        status,
                        assigned,
                        date2,

                        description,
                        edit_description_image_button,
                        description_image_button,
                    ],

                    spacing=12,

                    scroll=ft.ScrollMode.AUTO,

                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),

                padding=10,

                width=min(page.width * 0.9, 500),
                height=min(page.height * 0.75, 600),
            ),
        )

        def update_record(e):

            connection = sqlite3.connect(DATABASE_PATH)

            cursor = connection.cursor()

            cursor.execute("""
            UPDATE records
            SET
                date1 = ?,
                subject = ?,
                subject_images = ?,
                people = ?,
                history = ?,
                history_images = ?,
                follow_date = ?,
                status = ?,
                assigned = ?,
                date2 = ?,
                description = ?,
                description_images = ?
            WHERE id = ?
        """, (
            date1.value,
            subject.value,

            "|".join(subject_images),

            people.value,

            history.value,

            "|".join(history_images),

            follow_date.value,

            status.value or "",

            assigned.value,

            date2.value,

            description.value,

            "|".join(description_images),

            record[0]
        ))

            connection.commit()
            #########برای تست
            print("UPDATE SAVED")
            print("SUBJECT IMAGES:", subject_images)
            print("HISTORY IMAGES:", history_images)
            print("DESCRIPTION IMAGES:", description_images)
            ################
            connection.close()

            dialog.open = False

            refresh_table()

            page.update()

        def close_edit_dialog(e):

            dialog.open = False
            page.update()

        dialog.actions = [
            ft.TextButton(
                "لغو",
                on_click=close_edit_dialog,
            ),

            ft.ElevatedButton(
                "ذخیره تغییرات",
                on_click=update_record,
            ),

            delete_button,
        ]

        page.overlay.append(dialog)

        dialog.open = True

        page.update()

    #######################تابع سرچ

    def search_changed(e):
        nonlocal search_text

        search_text = e.control.value.strip()

        print("SEARCH TEXT:", repr(search_text))

        refresh_table()

########################### تابع مربوط به فیلتر رکورد ها
    def filter_records(records):

        keyword = search_text.casefold().strip()
        selected_status = status_filter.value

        filtered = []

        for record in records:

            # وضعیت رکورد
            record_status = (
                ""
                if record[8] is None
                else str(record[8]).strip()
            )

            # فیلتر وضعیت
            if (
                selected_status
                and selected_status != "همه"
                and record_status != selected_status
            ):
                continue

            # فیلتر جستجو
            if keyword:

                fields = [
                    record[1],
                    record[2],
                    record[4],
                    record[5],
                    record[7],
                    record[8],
                    record[9],
                    record[10],
                    record[11],
                ]

                text = " ".join(
                    ""
                    if value is None
                    else str(value)
                    for value in fields
                ).casefold()

                if keyword not in text:
                    continue

            filtered.append(record)

        return filtered
    ########################### تابع وضعیت
    def status_changed(e):
        refresh_table()

    ##########################
    def refresh_table():

        custom_table.controls.clear()

        all_records = load_records()

        records = filter_records(all_records)

        print("ALL RECORDS:", len(all_records))
        print("FILTERED RECORDS:", len(records))

        for record in records:
            custom_table.controls.append(
                create_table_row(record)
            )

        page.update()
    ##############################
    def open_add_dialog(e):
        

        date1 = ft.TextField(
            label="تاریخ اعلام موضوع"
        )

        subject = ft.TextField(
            label="شرح موضوع",
            multiline=True,
            min_lines=3,
            max_lines=6,
        )
            ############ جهت افزودن عکس

        subject_images = []
        history_images = []
        description_images = []

        async def add_subject_image(e):

            print("ADD IMAGE BUTTON CLICKED")

            files = await file_picker.pick_files(
                allow_multiple=True,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[
                    "png",
                    "jpg",
                    "jpeg"
                ],
            )

            if not files:
                print("NO FILE SELECTED")
                return

            print("FILES SELECTED:", len(files))

            os.makedirs(IMAGE_DIR, exist_ok=True)

            for file in files:

                print("FILE NAME:", file.name)
                print("FILE PATH:", file.path)

                if not file.path:
                    print("FILE PATH IS EMPTY")
                    continue

                filename = os.path.basename(file.path)

                destination = os.path.join(
                    IMAGE_DIR,
                    filename
                )

                shutil.copy2(
                    file.path,
                    destination
                )

                relative_path = os.path.join(
                    "images",
                    filename
                )

                subject_images.append(relative_path)

                print("SAVED:", destination)

            print("SUBJECT IMAGES:", subject_images)
        ########################
        async def add_history_image(e):

            print("ADD HISTORY IMAGE BUTTON CLICKED")

            files = await file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=[
                    "png",
                    "jpg",
                    "jpeg"
                ],
            )

            if not files:
                return

            for file in files:

                filename = os.path.basename(file.path)

                destination = os.path.join(
                    IMAGE_DIR,
                    filename
                )

                shutil.copy2(
                    file.path,
                    destination
                )

                history_images.append(
                    os.path.join(
                        "images",
                        filename
                    )
                )

                print("HISTORY IMAGE SAVED:", destination)
        #############################
        async def add_description_image(e):

            print("ADD DESCRIPTION IMAGE BUTTON CLICKED")

            files = await file_picker.pick_files(
                allow_multiple=True,
                allowed_extensions=[
                    "png",
                    "jpg",
                    "jpeg"
                ],
            )

            if not files:
                return

            for file in files:

                filename = os.path.basename(file.path)

                destination = os.path.join(
                    IMAGE_DIR,
                    filename
                )

                shutil.copy2(
                    file.path,
                    destination
                )

                description_images.append(
                    os.path.join(
                        "images",
                        filename
                    )
                )

                print("DESCRIPTION IMAGE SAVED:", destination)

        
        ###################
        subject_image_button = ft.ElevatedButton(
            "افزودن عکس",
            on_click=add_subject_image
        )
        #########افزودن عکس سوابق و توضیحات
        history_image_button = ft.ElevatedButton(
            "افزودن عکس سوابق",
            on_click=add_history_image
        )


        description_image_button = ft.ElevatedButton(
            "افزودن عکس توضیحات",
            on_click=add_description_image
        )

       ##############
        people = ft.TextField(
            label="اشخاص مرتبط"
        )

        history = ft.TextField(
            label="سوابق",
            multiline=True,
            min_lines=3,
            max_lines=6,
        )

        follow_date = ft.TextField(
            label="تاریخ انجام-پیگیری"
        )

        status = ft.Dropdown(
            label="وضعیت",
            options=[
                ft.DropdownOption("در حال بررسی"),
                ft.DropdownOption("در حال انجام"),
                ft.DropdownOption("انجام شد"),
                ft.DropdownOption("مختومه"),
            ],
        )

        assigned = ft.TextField(
            label="محول به"
        )

        date2 = ft.TextField(
            label="تاریخ"
        )

        description = ft.TextField(
            label="توضیحات",
            multiline=True,
            min_lines=3,
         max_lines=6,
        )
        #####################
        
#################
        dialog = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "ثبت اطلاعات",
                size=20,
            ),

            content=ft.Container(
                content=ft.Column(
                    [
                        date1,

                        subject,
                        subject_image_button,

                        people,

                        history,
                        history_image_button,

                        follow_date,
                        status,
                        assigned,
                        date2,

                        description,
                        description_image_button,
                    ],

                    spacing=12,

                    scroll=ft.ScrollMode.AUTO,

                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                ),

                padding=10,

                width=min(page.width * 0.9, 500),

                height=min(page.height * 0.75, 600),
            ),  
        )
        def save_new_record(e):

            print("SAVE BUTTON CLICKED")

            try:

                connection = sqlite3.connect(
                    DATABASE_PATH
                )

                cursor = connection.cursor()

                # ------------------------------------------
                # اطمینان از وجود ستون‌ها
                # ------------------------------------------

                cursor.execute(
                    "PRAGMA table_info(records)"
                )

                columns = [
                    row[1]
                    for row in cursor.fetchall()
                ]

                if "transfer_id" not in columns:

                    cursor.execute("""
                        ALTER TABLE records
                        ADD COLUMN transfer_id TEXT
                 """)

                if "data_hash" not in columns:

                    cursor.execute("""
                        ALTER TABLE records
                        ADD COLUMN data_hash TEXT
                    """)

                # ------------------------------------------
                # Transfer ID
                # ------------------------------------------

                transfer_id = str(
                    uuid.uuid4()
                )

                # ------------------------------------------
                # اطلاعات فرم
                # ------------------------------------------

                values = (
                    date1.value or "",
                    subject.value or "",
                    "|".join(subject_images),
                    people.value or "",
                    history.value or "",
                    "|".join(history_images),
                    follow_date.value or "",
                    status.value or "",
                    assigned.value or "",
                    date2.value or "",
                    description.value or "",
                    "|".join(description_images),
                )

                # ------------------------------------------
                # Hash
                # ------------------------------------------

                hash_source = "|".join(
                    str(value or "")
                    for value in values
                )

                data_hash = hashlib.sha256(
                    hash_source.encode("utf-8")
                ).hexdigest()

                # ------------------------------------------
                # INSERT
                # ------------------------------------------

                cursor.execute("""
                    INSERT INTO records (
                        date1,
                        subject,
                        subject_images,
                        people,
                        history,
                        history_images,
                        follow_date,
                        status,
                        assigned,
                        date2,
                        description,
                        description_images,
                        transfer_id,
                        data_hash
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?
                    )
                """, (
                    *values,
                    transfer_id,
                    data_hash
                ))

                connection.commit()

                print(
                    "RECORD SAVED:",
                    transfer_id
                )

                cursor.execute(
                    "SELECT COUNT(*) FROM records"
                )

                count = cursor.fetchone()[0]

                print(
                    "TOTAL RECORDS:",
                    count
                )

                connection.close()

                dialog.open = False

                refresh_table()

                page.update()

            except Exception as error:

                print(
                    "SAVE ERROR:",
                    error
                )

        def close_dialog(e):

            dialog.open = False

            page.update()

        dialog.actions = [
            ft.TextButton(
                "لغو",
                on_click=close_dialog,
            ),
            ft.ElevatedButton(
                "ذخیره",
                on_click=save_new_record,
            ),
        ]

        page.overlay.append(dialog)

        dialog.open = True

        page.update()

    

    
    #file_picker.on_result = lambda e: print("PICKER WORKED", e.files)

    def create_backup(e):

        print("BACKUP BUTTON CLICKED")

        try:
            import zipfile
            from datetime import datetime

            backup_dir = os.path.join(
                BASE_DIR,
                "backups"
            )

            os.makedirs(
                backup_dir,
                exist_ok=True
            )

            timestamp = datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )

            backup_file = os.path.join(
                backup_dir,
                f"AssetManager_Backup_{timestamp}.zip"
            )

            with zipfile.ZipFile(
                backup_file,
                "w",
                zipfile.ZIP_DEFLATED
            ) as backup_zip:

                # دیتابیس
                if os.path.exists(DATABASE_PATH):

                    backup_zip.write(
                        DATABASE_PATH,
                        arcname="database/database.db"
                    )

                # تصاویر
                if os.path.exists(IMAGE_DIR):

                    for root, dirs, files in os.walk(IMAGE_DIR):

                        for file in files:

                            full_path = os.path.join(
                                root,
                                file
                            )

                            relative_path = os.path.relpath(
                                full_path,
                                BASE_DIR
                            )

                            backup_zip.write(
                                full_path,
                                arcname=relative_path
                            )

            print(
                "BACKUP CREATED:",
                backup_file
            )

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "نسخه پشتیبان با موفقیت ایجاد شد"
                )
            )

            page.snack_bar.open = True

            page.update()

        except Exception as error:

            print(
                "BACKUP ERROR:",
                error
            )

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    f"خطا در ایجاد نسخه پشتیبان: {error}"
                )
            )

            page.snack_bar.open = True

            page.update()
    ##################################
    async def create_transfer_package(e):

        print("TRANSFER PACKAGE BUTTON CLICKED")

        try:
            import zipfile
            from datetime import datetime
            import json
            import tempfile
            import os
            import shutil

            # ==================================================
            # نام بسته انتقال
            # ==================================================

            timestamp = datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )

            package_name = (
                f"AssetManager_Transfer_{timestamp}.zip"
            )

            # ==================================================
            # ساخت بسته موقت
            # ==================================================

            temp_dir = tempfile.gettempdir()

            temp_package_file = os.path.join(
                temp_dir,
                package_name
            )

            transfer_info = {
                "package_type": "AssetManager_Transfer",
                "format_version": 1
            }

            with zipfile.ZipFile(
                temp_package_file,
                "w",
                zipfile.ZIP_DEFLATED
            ) as package_zip:

                # ------------------------------------------
                # اطلاعات بسته
                # ------------------------------------------

                package_zip.writestr(
                    "transfer_info.json",
                    json.dumps(
                        transfer_info,
                        ensure_ascii=False,
                        indent=4
                    )
                )

                # ------------------------------------------
                # دیتابیس
                # ------------------------------------------

                if os.path.exists(DATABASE_PATH):

                    package_zip.write(
                        DATABASE_PATH,
                        arcname="database/database.db"
                    )

                # ------------------------------------------
                # تصاویر
                # ------------------------------------------

                if os.path.exists(IMAGE_DIR):

                    for root, dirs, files in os.walk(
                        IMAGE_DIR
                    ):

                        for file in files:

                            full_path = os.path.join(
                                root,
                                file
                            )

                            relative_path = os.path.relpath(
                                full_path,
                                BASE_DIR
                            )

                            package_zip.write(
                                full_path,
                                arcname=relative_path
                            )

            print(
                "TEMP TRANSFER PACKAGE CREATED:",
                temp_package_file
            )

            # ==================================================
            # پرسیدن مسیر ذخیره از کاربر
            # ==================================================

            save_path = await file_picker.save_file(
                dialog_title="ذخیره بسته انتقال",
                file_name=package_name,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["zip"],
            )

            # ==================================================
            # کاربر لغو کرده
            # ==================================================

            if not save_path:

                print(
                    "TRANSFER PACKAGE SAVE CANCELLED"
                )

                try:
                    os.remove(temp_package_file)
                except Exception:
                    pass

                return

            print(
                "USER SELECTED SAVE PATH:",
                save_path
            )

            # ==================================================
            # انتقال بسته موقت به مسیر انتخاب‌شده
            # ==================================================

            shutil.copy2(
                temp_package_file,
                save_path
            )

            # ==================================================
            # حذف فایل موقت
            # ==================================================

            try:
                os.remove(temp_package_file)
            except Exception:
                pass

            print(
                "TRANSFER PACKAGE SAVED:",
                save_path
            )

            # ==================================================
            # پیام موفقیت
            # ==================================================

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "بسته انتقال با موفقیت ذخیره شد"
                )
            )

            page.snack_bar.open = True

            page.update()

        except Exception as error:

            print(
                "TRANSFER PACKAGE ERROR:",
                error
            )

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    f"خطا در ایجاد بسته انتقال: {error}"
                )
            )

            page.snack_bar.open = True

            page.update()


    #############################
    async def restore_transfer_package(
            e,
            selected_backup=None
        ):

        print("RESTORE BUTTON CLICKED")

        try:
            import zipfile
            import json

            # ==================================================
            # اگر Backup از پنجره مدیریت انتخاب شده
            # ==================================================

            if selected_backup:

                package_path = selected_backup

                print(
                    "SELECTED BACKUP PACKAGE:",
                    package_path
                )

                await process_transfer_package(
                    package_path
                )

                return

            # ==================================================
            # بازیابی عادی از FilePicker
            # ==================================================

            print(
                "OPENING TRANSFER FILE PICKER"
            )

            files = await file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["zip"],
            )

            if not files:

                print(
                    "NO TRANSFER FILE SELECTED"
                )

                return

            package_path = files[0].path

            if not package_path:

                print(
                    "TRANSFER PACKAGE PATH IS EMPTY"
                )

                return

            print(
                "TRANSFER PACKAGE SELECTED:",
                package_path
            )

            await process_transfer_package(
                package_path
            )

        except Exception as error:

            print(
                "RESTORE ERROR:",
                error
            )

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    f"خطا در بازیابی: {error}"
                )
            )

            page.snack_bar.open = True

            page.update()
    ##############################################
    async def process_transfer_package(
        package_path
    ):

        import zipfile
        import json

        try:

            print(
                "PROCESSING PACKAGE:",
                package_path
            )

            # ==============================
            # بررسی بسته
            # ==============================

            with zipfile.ZipFile(
                package_path,
                "r"
            ) as package_zip:

                package_files = (
                    package_zip.namelist()
                )

                if "transfer_info.json" not in package_files:

                    raise Exception(
                        "transfer_info.json پیدا نشد."
                    )

                transfer_info = json.loads(
                    package_zip.read(
                        "transfer_info.json"
                    ).decode("utf-8")
                )

                if transfer_info.get(
                    "package_type"
                ) != "AssetManager_Transfer":

                    raise Exception(
                        "این فایل بسته انتقال معتبر نیست."
                    )

                if transfer_info.get(
                    "format_version"
                ) != 1:

                    raise Exception(
                        "نسخه بسته انتقال پشتیبانی نمی‌شود."
                    )

            # ==============================
            # انتخاب حالت بازیابی
            # ==============================

            def select_mode(mode):

                mode_dialog.open = False

                page.update()

                if mode == "merge":

                    page.run_task(
                        perform_transfer_restore,
                        package_path,
                        "merge"
                    )

                elif mode == "replace":

                    page.run_task(
                        perform_transfer_restore,
                        package_path,
                        "replace"
                    )

            mode_dialog = ft.AlertDialog(
                modal=True,

                title=ft.Text(
                    "نحوه بازیابی اطلاعات"
                ),

                content=ft.Text(
                    "اطلاعات بسته انتقال چگونه بازیابی شود؟"
                ),

                actions=[

                    ft.TextButton(
                        "ادغام اطلاعات",
                        on_click=lambda e:
                            select_mode("merge")
                    ),

                    ft.TextButton(
                        "جایگزینی کامل",
                        on_click=lambda e:
                            select_mode("replace")
                    ),

                    ft.TextButton(
                        "لغو",
                        on_click=lambda e:
                            select_mode("cancel")
                    ),
                ],
            )

            page.overlay.append(
                mode_dialog
            )

            mode_dialog.open = True

            page.update()

        except Exception as error:

            print(
                "PACKAGE PROCESS ERROR:",
                error
            )

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    f"خطا در بررسی بسته: {error}"
                )
            )

            page.snack_bar.open = True

            page.update()

    ##########################################
    async def perform_transfer_restore(
        package_path,
        mode
    ):

        print(
            "RESTORE MODE:",
            mode
        )

        temp_dir = None

        try:

            import zipfile
            import tempfile
            import uuid

            temp_dir = tempfile.mkdtemp(
                prefix="assetmanager_transfer_"
            )

            # ==============================
            # Extract
            # ==============================

            with zipfile.ZipFile(
                package_path,
                "r"
            ) as package_zip:

                package_zip.extractall(
                    temp_dir
                )

            package_database = os.path.join(
                temp_dir,
                "database",
                "database.db"
            )

            package_images = os.path.join(
                temp_dir,
                "images"
            )

            if not os.path.exists(
                package_database
            ):

                raise Exception(
                    "database/database.db داخل بسته پیدا نشد."
                )

            # ==============================
            # مسیرهای فعلی
            # ==============================

            current_database = DATABASE_PATH
            current_images = IMAGE_DIR

            os.makedirs(
                os.path.dirname(
                    current_database
                ),
                exist_ok=True
            )

            os.makedirs(
                current_images,
                exist_ok=True
            )

            # ==================================================
            # REPLACE
            # ==================================================

            if mode == "replace":

                print(
                    "REPLACING CURRENT DATA"
                )

                # پشتیبان قبل از جایگزینی
                backup_dir = os.path.join(
                    BASE_DIR,
                    "backups"
                )

                os.makedirs(
                    backup_dir,
                    exist_ok=True
                )

                # دیتابیس فعلی
                if os.path.exists(
                    current_database
                ):

                    shutil.copy2(
                        current_database,
                        os.path.join(
                            backup_dir,
                            "database_before_transfer.db"
                        )
                    )

                # تصاویر فعلی
                if os.path.exists(
                    current_images
                ):

                    backup_images = os.path.join(
                        backup_dir,
                        "images_before_transfer"
                    )

                    if os.path.exists(
                        backup_images
                    ):

                        shutil.rmtree(
                            backup_images
                        )

                    shutil.copytree(
                        current_images,
                        backup_images
                    )

                # جایگزینی دیتابیس
                shutil.copy2(
                    package_database,
                    current_database
                )

                # جایگزینی تصاویر
                if os.path.exists(
                    package_images
                ):

                    if os.path.exists(
                        current_images
                    ):

                        shutil.rmtree(
                            current_images
                        )

                    shutil.copytree(
                        package_images,
                        current_images
                    )

            # ==================================================
            # MERGE
            # ==================================================

            elif mode == "merge":

                print("MERGING TRANSFER DATA")

                conn_current = sqlite3.connect(
                    current_database
                )

                conn_package = sqlite3.connect(
                    package_database
                )

                cur_current = conn_current.cursor()
                cur_package = conn_package.cursor()

                os.makedirs(
                    current_images,
                    exist_ok=True
                )

                # ------------------------------------------
                # اطمینان از وجود data_hash
                # ------------------------------------------

                cur_current.execute(
                    "PRAGMA table_info(records)"
                )

                current_columns = [
                    row[1]
                    for row in cur_current.fetchall()
                ]

                if "transfer_id" not in current_columns:

                    cur_current.execute("""
                        ALTER TABLE records
                        ADD COLUMN transfer_id TEXT
                    """)

                if "data_hash" not in current_columns:

                    cur_current.execute("""
                        ALTER TABLE records
                        ADD COLUMN data_hash TEXT
                    """)

                # ------------------------------------------
                # بررسی ستون‌های دیتابیس بسته
                # ------------------------------------------

                cur_package.execute(
                    "PRAGMA table_info(records)"
                )

                package_columns = [
                    row[1]
                    for row in cur_package.fetchall()
                ]

                has_data_hash = (
                    "data_hash" in package_columns
                )

                has_transfer_id = (
                    "transfer_id" in package_columns
                )

                # ------------------------------------------
                # خواندن رکوردهای بسته
                # ------------------------------------------

                if has_data_hash and has_transfer_id:

                    cur_package.execute("""
                        SELECT
                            date1,
                            subject,
                            subject_images,
                            people,
                            history,
                            history_images,
                            follow_date,
                            status,
                            assigned,
                            date2,
                            description,
                            description_images,
                            transfer_id,
                            data_hash
                        FROM records
                    """)

                else:

                    cur_package.execute("""
                        SELECT
                            date1,
                            subject,
                            subject_images,
                            people,
                            history,
                            history_images,
                            follow_date,
                            status,
                            assigned,
                            date2,
                            description,
                            description_images
                        FROM records
                    """)

                package_records = (
                    cur_package.fetchall()
                )

                print(
                    "TRANSFER RECORDS:",
                    len(package_records)
                )

                # ------------------------------------------
                # انتقال تصاویر
                # ------------------------------------------

                def transfer_images(image_string):

                    if not image_string:
                        return ""

                    image_list = [
                        img
                        for img in image_string.split("|")
                        if img
                    ]

                    new_images = []

                    for image_path in image_list:

                        source_path = os.path.join(
                            temp_dir,
                            image_path
                        )

                        if not os.path.exists(
                            source_path
                        ):

                            print(
                                "IMAGE NOT FOUND:",
                                source_path
                            )

                            continue

                        original_name = (
                            os.path.basename(
                                image_path
                            )
                        )

                        destination_name = (
                            original_name
                        )

                        destination_path = os.path.join(
                            current_images,
                            destination_name
                        )

                        # جلوگیری از overwrite
                        if os.path.exists(
                            destination_path
                        ):

                            name, extension = (
                                os.path.splitext(
                                    original_name
                                )
                            )

                            destination_name = (
                                f"{name}_"
                                f"{uuid.uuid4().hex[:8]}"
                                f"{extension}"
                            )

                            destination_path = (
                                os.path.join(
                                    current_images,
                                    destination_name
                                )
                            )

                        shutil.copy2(
                            source_path,
                            destination_path
                        )

                        new_images.append(
                            os.path.join(
                                "images",
                                destination_name
                            ).replace(
                                "\\",
                                "/"
                            )
                        )

                    return "|".join(
                        new_images
                    )

                # ------------------------------------------
                # MERGE
                # ------------------------------------------

                for record in package_records:

                    # --------------------------------------
                    # رکوردهای جدید با data_hash
                    # --------------------------------------

                    if has_data_hash and has_transfer_id:

                        (
                            date1,
                            subject,
                            subject_images,
                            people,
                            history,
                            history_images,
                            follow_date,
                            status,
                            assigned,
                            date2,
                            description,
                            description_images,
                            transfer_id,
                            data_hash
                        ) = record

                    else:

                        (
                            date1,
                            subject,
                            subject_images,
                            people,
                            history,
                            history_images,
                            follow_date,
                            status,
                            assigned,
                            date2,
                            description,
                            description_images
                        ) = record

                        transfer_id = str(
                            uuid.uuid4()
                        )

                        # ساخت hash برای بسته‌های قدیمی
                        hash_source = "|".join([
                            str(date1 or ""),
                            str(subject or ""),
                            str(subject_images or ""),
                            str(people or ""),
                            str(history or ""),
                            str(history_images or ""),
                            str(follow_date or ""),
                            str(status or ""),
                            str(assigned or ""),
                            str(date2 or ""),
                            str(description or ""),
                            str(description_images or "")
                        ])

                        data_hash = hashlib.sha256(
                            hash_source.encode("utf-8")
                        ).hexdigest()

                    # --------------------------------------
                    # بررسی transfer_id
                    # --------------------------------------

                    cur_current.execute("""
                        SELECT
                            id,
                            data_hash
                        FROM records
                        WHERE transfer_id = ?
                    """, (
                        transfer_id,
                    ))

                    existing_record = (
                        cur_current.fetchone()
                    )

                    # --------------------------------------
                    # رکورد وجود دارد
                    # --------------------------------------

                    if existing_record:

                        existing_id = (
                            existing_record[0]
                        )

                        existing_hash = (
                            existing_record[1]
                        )

                        # ----------------------------------
                        # بدون تغییر → SKIP
                        # ----------------------------------

                        if existing_hash == data_hash:

                            print(
                                "DUPLICATE RECORD SKIPPED:",
                                transfer_id
                            )

                            continue

                        # ----------------------------------
                        # تغییر کرده → UPDATE
                        # ----------------------------------

                        print(
                            "UPDATED RECORD:",
                            transfer_id
                        )

                        new_subject_images = (
                            transfer_images(
                                subject_images
                            )
                        )

                        new_history_images = (
                            transfer_images(
                                history_images
                            )
                        )

                        new_description_images = (
                            transfer_images(
                                description_images
                            )
                        )

                        cur_current.execute("""
                            UPDATE records SET

                                date1=?,
                                subject=?,
                                subject_images=?,
                                people=?,
                                history=?,
                                history_images=?,
                                follow_date=?,
                                status=?,
                                assigned=?,
                                date2=?,
                                description=?,
                                description_images=?,
                                transfer_id=?,
                                data_hash=?

                            WHERE id=?
                        """, (
                            date1 or "",
                            subject or "",
                            new_subject_images,
                            people or "",
                            history or "",
                            new_history_images,
                            follow_date or "",
                            status or "",
                            assigned or "",
                            date2 or "",
                            description or "",
                            new_description_images,
                            transfer_id,
                            data_hash,
                            existing_id
                        ))

                        continue

                    # --------------------------------------
                    # رکورد جدید → INSERT
                    # --------------------------------------

                    print(
                        "NEW RECORD INSERTED:",
                        transfer_id
                    )

                    new_subject_images = (
                        transfer_images(
                            subject_images
                        )
                    )

                    new_history_images = (
                        transfer_images(
                            history_images
                        )
                    )

                    new_description_images = (
                        transfer_images(
                            description_images
                        )
                    )

                    cur_current.execute("""
                        INSERT INTO records (
                            date1,
                            subject,
                            subject_images,
                            people,
                            history,
                            history_images,
                            follow_date,
                            status,
                            assigned,
                            date2,
                            description,
                            description_images,
                            transfer_id,
                            data_hash
                        )
                        VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?
                        )
                    """, (
                        date1 or "",
                        subject or "",
                        new_subject_images,
                        people or "",
                        history or "",
                        new_history_images,
                        follow_date or "",
                        status or "",
                        assigned or "",
                        date2 or "",
                        description or "",
                        new_description_images,
                        transfer_id,
                        data_hash
                    ))

                # ------------------------------------------
                # پایان Merge
                # ------------------------------------------

                conn_current.commit()

                conn_package.close()
                conn_current.close()
            # ==============================
            # Refresh
            # ==============================

            refresh_table()

            print(
                "TRANSFER RESTORE COMPLETED"
            )

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    "بازیابی اطلاعات با موفقیت انجام شد"
                )
            )

            page.snack_bar.open = True

            page.update()

        except Exception as error:

            print(
                "TRANSFER RESTORE ERROR:",
                error
            )

            page.snack_bar = ft.SnackBar(
                ft.Text(
                    f"خطا در بازیابی: {error}"
                )
            )

            page.snack_bar.open = True

            page.update()

        finally:

            if temp_dir and os.path.exists(
                temp_dir
            ):

                shutil.rmtree(
                    temp_dir,
                    ignore_errors=True
                )
    #############################
    def manage_backups(e):

        print("MANAGE BACKUPS CLICKED")

        backup_dir = os.path.join(
            BASE_DIR,
            "backups"
        )

        os.makedirs(
            backup_dir,
            exist_ok=True
        )

        backup_files = []

        for file_name in os.listdir(
            backup_dir
        ):

            full_path = os.path.join(
                backup_dir,
                file_name
            )

            if (
                os.path.isfile(full_path)
                and file_name.lower().endswith(".zip")
            ):

                backup_files.append(
                    full_path
                )

        backup_files.sort(
            key=os.path.getmtime,
            reverse=True
        )

        backup_list = ft.ListView(
            expand=True,
            spacing=8,
        )

        if not backup_files:

            backup_list.controls.append(
                ft.Text(
                    "هیچ نسخه پشتیبانی وجود ندارد.",
                    text_align=ft.TextAlign.CENTER,
                )
            )

        else:

            for file_path in backup_files:

                file_name = os.path.basename(
                    file_path
                )

                modified_time = datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                backup_list.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            file_name,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            modified_time,
                                            size=11,
                                        ),
                                    ],
                                    expand=True,
                                    spacing=3,
                                ),

                                ft.ElevatedButton(
                                    "بازیابی",
                                    on_click=lambda e, path=file_path:
                                        restore_backup_file(path),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),

                        padding=10,

                        border=ft.Border.all(1),

                        border_radius=8,
                    )
                )

        close_button = ft.TextButton(
            "بستن",
            on_click=lambda e: close_backup_dialog(),
        )
        #################
        def restore_backup_file(file_path):

            print(
                "RESTORE SELECTED BACKUP:",
                file_path
            )

            answer = ft.AlertDialog(
                modal=True,

                title=ft.Text(
                    "تأیید بازیابی"
                ),

                content=ft.Text(
                    "آیا می‌خواهید این نسخه پشتیبان بازیابی شود؟\n\n"
                    + os.path.basename(file_path)
                ),

                actions=[
                    ft.TextButton(
                        "خیر",
                    ),

                    ft.ElevatedButton(
                        "بله، بازیابی کن",
                        on_click=lambda e:
                            confirm_restore_backup(
                                file_path,
                                answer
                            ),
                    ),
                ],
            )

            page.overlay.append(
                answer
            )

            answer.open = True

            page.update()
        #################
        def confirm_restore_backup(
            file_path,
            dialog
        ):

            print(
                "CONFIRMED BACKUP RESTORE:",
                file_path
            )

            dialog.open = False

            page.update()

            restore_transfer_package(
                None,
                selected_backup=file_path
            )


        ###################

        def close_backup_dialog():

            backup_dialog.open = False

            page.update()

        backup_dialog = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "مدیریت نسخه‌های پشتیبان"
            ),

            content=ft.Container(
                content=backup_list,
                width=600,
                height=450,
            ),

            actions=[
                close_button,
            ],
        )

        page.overlay.append(
            backup_dialog
        )

        backup_dialog.open = True

        page.update()
    
    #################
    add_button = ft.ElevatedButton(
        "ثبت اطلاعات",
        on_click=open_add_dialog,
    )

    backup_button = ft.ElevatedButton(
        "نسخه پشتیبان",
        on_click=create_backup,
    )

    manage_backup_button = ft.ElevatedButton(
        "مدیریت پشتیبان‌ها",
        on_click=manage_backups,
    )

    restore_button = ft.ElevatedButton(
        "بازیابی",
        on_click=restore_transfer_package,
    )

    package_button = ft.ElevatedButton(
        "بسته انتقال",
        on_click=create_transfer_package,
    )

    buttons = ft.Row(
        [
            add_button,
            backup_button,
            manage_backup_button,
            restore_button,
            package_button,
        ],
        wrap=True,
        spacing=10,
    )

########################### اضافه کردن جستجو 

    search_box = ft.TextField(
        hint_text="جستجو در اطلاعات...",
        prefix_icon=ft.Icons.SEARCH,
        height=45,
        #width=300,
        text_size=14,
        on_change=search_changed,
    )

    ############################فیلتر وضعیت
    status_filter = ft.Dropdown(
        label="وضعیت",
        width=160,
        value="همه",
        options=[
            ft.DropdownOption(key="همه", text="همه"),
            ft.DropdownOption(key="انجام شد", text="انجام شد"),
            ft.DropdownOption(key="در حال انجام", text="در حال انجام"),
            ft.DropdownOption(key="در حال بررسی", text="در حال بررسی"),
            ft.DropdownOption(key="مختومه", text="مختومه"),
        ],
        on_select=lambda e: status_changed(e),
    )

#############################
    table_width = max(page.width or 400, 1390)
  
    

    page.controls.clear()
    page.update()
    

    page.add(
        title,
        ft.Divider(),
        buttons,
        ft.Divider(),

        ft.Container(
            padding=10,

            margin=ft.Margin.only(
                right=30,
            ),

            content=ft.Row(
                controls=[
                    ft.Container(
                        expand=True,
                        content=search_box,
                    ),

                    status_filter,
                ],

                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
        ),

        ft.Container(
            height=600,
            expand=True,

            content=ft.Row(
                controls=[
                    ft.Container(
                        width=TABLE_WIDTH,
                        height=600,

                        margin=ft.Margin.only(
                            right=30,
                        ),

                        content=ft.Column(
                            controls=[
                                create_table_header(),

                                ft.Container(
                                    expand=True,
                                    width=TABLE_WIDTH,
                                    content=custom_table,
                                ),
                            ],

                            spacing=0,
                            expand=True,
                        ),
                    ),
                ],

                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),

            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        ),
    )

    refresh_table()
    

    print(
        "VISIBLE CONTROLS:",
        len(custom_table.controls)
    )

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")