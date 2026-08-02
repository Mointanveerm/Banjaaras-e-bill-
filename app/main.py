import os
from datetime import datetime
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar

# Request storage permissions on Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

KV = '''
MDScreenManager:
    InputScreen:
    BillScreen:

<InputScreen>:
    name: 'input'
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "15dp"

        MDLabel:
            text: "Banjaara's Catering"
            font_style: "H4"
            halign: "center"
            theme_text_color: "Primary"
            
        MDLabel:
            text: "Compromise on health? Why?"
            font_style: "Subtitle1"
            halign: "center"
            theme_text_color: "Secondary"

        MDTextField:
            id: client_name
            hint_text: "Bill To (Company/Client Name)"
            mode: "rectangle"

        MDTextField:
            id: price_per_roti
            hint_text: "Price per Roti (in Rs @rs)"
            mode: "rectangle"
            input_filter: "float"

        MDBoxLayout:
            orientation: 'horizontal'
            spacing: "10dp"
            size_hint_y: None
            height: "60dp"
            
            MDTextField:
                id: slot_date
                hint_text: "Date (e.g., 1-8-26)"
                mode: "rectangle"
            
            MDTextField:
                id: slot_qty
                hint_text: "Amount of Roti"
                mode: "rectangle"
                input_filter: "int"
                
            MDRaisedButton:
                text: "Add Slot"
                on_release: root.add_slot()

        ScrollView:
            MDBoxLayout:
                id: slots_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: "5dp"

        MDRaisedButton:
            text: "Generate E-Bill"
            pos_hint: {"center_x": .5}
            on_release: root.generate_bill()

<BillScreen>:
    name: 'bill'
    MDBoxLayout:
        orientation: 'vertical'
        
        # This is the container that will be exported to PNG
        MDBoxLayout:
            id: bill_container
            orientation: 'vertical'
            padding: "30dp"
            spacing: "10dp"
            md_bg_color: 1, 1, 1, 1
            
            MDLabel:
                text: "BANJAARA'S CATERING"
                font_style: "H4"
                halign: "center"
                bold: True
                
            MDLabel:
                text: "Compromise on health? Why?"
                font_style: "Caption"
                halign: "center"
                
            MDLabel:
                id: bill_client_name
                text: "Billed To: "
                font_style: "Subtitle1"
                bold: True
                
            MDBoxLayout:
                size_hint_y: None
                height: "2dp"
                md_bg_color: 0, 0, 0, 1
                
            ScrollView:
                MDBoxLayout:
                    id: bill_items
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
            
            MDBoxLayout:
                size_hint_y: None
                height: "2dp"
                md_bg_color: 0, 0, 0, 1
                
            MDLabel:
                id: bill_total
                text: "Total Amount: Rs 0"
                font_style: "H6"
                halign: "right"
                bold: True

            MDLabel:
                text: "Banjaara's e-bill services 🌍"
                theme_text_color: "Custom"
                text_color: 0, 0.6, 0, 1  # Green Color
                halign: "center"
                bold: True
                
            MDLabel:
                text: "Regards,\\nSYED TANVEER HUSSAIN\\nPh no: 03230007773"
                font_style: "Caption"
                halign: "left"
        
        MDBoxLayout:
            size_hint_y: None
            height: "60dp"
            padding: "10dp"
            spacing: "20dp"
            
            MDRaisedButton:
                text: "Back"
                on_release: app.root.current = 'input'
                
            MDRaisedButton:
                text: "Download PNG"
                md_bg_color: 0, 0.6, 0, 1
                on_release: root.download_png()
'''

class InputScreen(MDScreen):
    slots = []

    def add_slot(self):
        if len(self.slots) >= 30:
            Snackbar(text="Maximum 30 slots reached!").open()
            return
            
        date_txt = self.ids.slot_date.text
        qty_txt = self.ids.slot_qty.text
        
        if date_txt and qty_txt:
            self.slots.append({"date": date_txt, "qty": int(qty_txt)})
            lbl = MDLabel(text=f"{date_txt} :: #{qty_txt} roti", size_hint_y=None, height="30dp")
            self.ids.slots_list.add_widget(lbl)
            self.ids.slot_date.text = ""
            self.ids.slot_qty.text = ""

    def generate_bill(self):
        app = MDApp.get_running_app()
        bill_screen = app.root.get_screen('bill')
        
        # Populate Bill Data
        client = self.ids.client_name.text or "Walk-in Client"
        price_str = self.ids.price_per_roti.text or "0"
        price = float(price_str)
        
        bill_screen.ids.bill_client_name.text = f"Billed To: {client}"
        bill_screen.ids.bill_items.clear_widgets()
        
        total_qty = 0
        for slot in self.slots:
            item_lbl = MDLabel(
                text=f"{slot['date']} :: #{slot['qty']} roti @ Rs {price}",
                size_hint_y=None, height="30dp"
            )
            bill_screen.ids.bill_items.add_widget(item_lbl)
            total_qty += slot['qty']
            
        grand_total = total_qty * price
        bill_screen.ids.bill_total.text = f"Total Amount: Rs {grand_total:.2f}"
        
        app.root.current = 'bill'

class BillScreen(MDScreen):
    def download_png(self):
        filename = f"Banjaras_Bill_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # Handle Android storage path
        if platform == 'android':
            path = os.path.join('/storage/emulated/0/Download', filename)
        else:
            path = filename
            
        # Export the specific bill container to PNG
        self.ids.bill_container.export_to_png(path)
        Snackbar(text=f"Bill saved to Downloads!").open()

class BanjaarasApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

if __name__ == '__main__':
    BanjaarasApp().run()
      
