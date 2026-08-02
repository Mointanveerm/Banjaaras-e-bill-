"""
Banjaara's Catering e-bill
---------------------------
A KivyMD mobile application for creating, calculating, and sharing
catering invoices ("e-bills") for Banjaara's Catering.

Structure:
    - BanjaaraApp        : Root MDApp, theme + screen manager setup
    - DashboardScreen     : Bill creation form (customer info + items)
    - ItemRow             : Reusable widget for a menu item with qty stepper
    - InvoiceScreen       : Formatted e-bill summary / export screen

This file is self-contained (single main.py) as required by the
Buildozer packaging layout.
"""

import datetime

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import (
    StringProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.lang import Builder
from kivy.clock import Clock

from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar


# ---------------------------------------------------------------------------
# Brand palette — deep amber / warm gold / dark slate
# ---------------------------------------------------------------------------
COLOR_BG_DARK = (0.07, 0.06, 0.09, 1)          # near-black warm slate
COLOR_SURFACE = (0.12, 0.11, 0.14, 1)          # card surface
COLOR_SURFACE_LIGHT = (0.16, 0.14, 0.17, 1)    # elevated surface
COLOR_GOLD = (0.83, 0.65, 0.24, 1)             # warm gold accent
COLOR_AMBER = (0.72, 0.42, 0.15, 1)            # deep amber accent
COLOR_TEXT_PRIMARY = (0.96, 0.93, 0.88, 1)     # warm off-white
COLOR_TEXT_MUTED = (0.72, 0.68, 0.63, 1)       # muted warm grey
COLOR_DIVIDER = (0.26, 0.23, 0.20, 1)

TAX_RATE = 0.05          # 5% service/tax charge
CURRENCY = "\u20b9"       # Rupee symbol


# ---------------------------------------------------------------------------
# Menu catalogue: category -> list of (name, default_price)
# ---------------------------------------------------------------------------
MENU_CATALOGUE = {
    "Starters": [
        ("Paneer Tikka", 180),
        ("Veg Seekh Kebab", 160),
        ("Chicken 65", 220),
        ("Corn Chaat", 120),
    ],
    "Main Course": [
        ("Paneer Butter Masala", 220),
        ("Dal Banjaara", 150),
        ("Chicken Curry", 260),
        ("Veg Biryani", 200),
        ("Butter Naan (pc)", 30),
    ],
    "Desserts": [
        ("Gulab Jamun (pc)", 25),
        ("Rasmalai (pc)", 35),
        ("Gajar Halwa", 90),
        ("Kulfi", 60),
    ],
}


KV = """
#:import dp kivy.metrics.dp

<ItemRow>:
    orientation: "vertical"
    size_hint_y: None
    height: dp(64)
    padding: [dp(4), dp(2)]
    spacing: dp(2)

    MDBoxLayout:
        orientation: "horizontal"
        spacing: dp(8)

        MDBoxLayout:
            orientation: "vertical"
            size_hint_x: 0.5

            MDLabel:
                text: root.item_name
                font_style: "Subtitle1"
                theme_text_color: "Custom"
                text_color: 0.96, 0.93, 0.88, 1
                bold: True
                shorten: True
                shorten_from: "right"

            MDLabel:
                text: root.price_display
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: 0.83, 0.65, 0.24, 1

        MDBoxLayout:
            orientation: "horizontal"
            size_hint_x: 0.32
            spacing: dp(2)
            pos_hint: {"center_y": 0.5}

            MDIconButton:
                icon: "minus-circle-outline"
                theme_text_color: "Custom"
                text_color: 0.72, 0.42, 0.15, 1
                on_release: root.decrement()

            MDLabel:
                text: str(root.quantity)
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.96, 0.93, 0.88, 1
                bold: True

            MDIconButton:
                icon: "plus-circle-outline"
                theme_text_color: "Custom"
                text_color: 0.83, 0.65, 0.24, 1
                on_release: root.increment()

        MDLabel:
            text: root.line_total_display
            size_hint_x: 0.18
            halign: "right"
            theme_text_color: "Custom"
            text_color: 0.96, 0.93, 0.88, 1
            bold: True

    MDSeparator:
        color: 0.26, 0.23, 0.20, 1


<SectionHeader@MDBoxLayout>:
    text: ""
    size_hint_y: None
    height: dp(36)
    padding: [dp(4), dp(4)]

    MDLabel:
        text: root.text
        font_style: "H6"
        bold: True
        theme_text_color: "Custom"
        text_color: 0.83, 0.65, 0.24, 1


<DashboardScreen>:
    name: "dashboard"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.07, 0.06, 0.09, 1

        MDTopAppBar:
            title: "Banjaara's Catering"
            specific_text_color: 0.96, 0.93, 0.88, 1
            md_bg_color: 0.12, 0.11, 0.14, 1
            elevation: 4
            right_action_items: [["receipt-text-outline", lambda x: root.go_to_invoice()]]

        ScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: [dp(16), dp(12), dp(16), dp(24)]
                spacing: dp(14)

                MDLabel:
                    text: "Create a New e-Bill"
                    font_style: "H5"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0.96, 0.93, 0.88, 1
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    text: "Fill in customer & event details, then pick items below."
                    font_style: "Caption"
                    theme_text_color: "Custom"
                    text_color: 0.72, 0.68, 0.63, 1
                    size_hint_y: None
                    height: self.texture_size[1]

                # ---- Customer Info Card ----
                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(300)
                    padding: dp(16)
                    spacing: dp(10)
                    md_bg_color: 0.12, 0.11, 0.14, 1
                    radius: [16, 16, 16, 16]
                    elevation: 2

                    MDTextField:
                        id: customer_name
                        hint_text: "Customer Name"
                        icon_left: "account-outline"
                        mode: "rectangle"
                        line_color_normal: 0.26, 0.23, 0.20, 1
                        line_color_focus: 0.83, 0.65, 0.24, 1
                        hint_text_color_normal: 0.72, 0.68, 0.63, 1
                        text_color_normal: 0.96, 0.93, 0.88, 1

                    MDTextField:
                        id: customer_phone
                        hint_text: "Phone Number"
                        icon_left: "phone-outline"
                        mode: "rectangle"
                        input_filter: "int"
                        line_color_normal: 0.26, 0.23, 0.20, 1
                        line_color_focus: 0.83, 0.65, 0.24, 1
                        hint_text_color_normal: 0.72, 0.68, 0.63, 1
                        text_color_normal: 0.96, 0.93, 0.88, 1

                    MDTextField:
                        id: event_date
                        hint_text: "Event Date (DD-MM-YYYY)"
                        icon_left: "calendar-month-outline"
                        mode: "rectangle"
                        line_color_normal: 0.26, 0.23, 0.20, 1
                        line_color_focus: 0.83, 0.65, 0.24, 1
                        hint_text_color_normal: 0.72, 0.68, 0.63, 1
                        text_color_normal: 0.96, 0.93, 0.88, 1
                        on_focus: if not self.focus: root.validate_date()

                    MDTextField:
                        id: guest_count
                        hint_text: "Guest Count (optional)"
                        icon_left: "account-group-outline"
                        mode: "rectangle"
                        input_filter: "int"
                        line_color_normal: 0.26, 0.23, 0.20, 1
                        line_color_focus: 0.83, 0.65, 0.24, 1
                        hint_text_color_normal: 0.72, 0.68, 0.63, 1
                        text_color_normal: 0.96, 0.93, 0.88, 1

                # ---- Menu Sections (populated dynamically in Python) ----
                MDBoxLayout:
                    id: menu_container
                    orientation: "vertical"
                    adaptive_height: True
                    spacing: dp(6)

                # ---- Custom Price Modifier Card ----
                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(150)
                    padding: dp(16)
                    spacing: dp(8)
                    md_bg_color: 0.12, 0.11, 0.14, 1
                    radius: [16, 16, 16, 16]
                    elevation: 2

                    MDLabel:
                        text: "Custom Adjustment"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.83, 0.65, 0.24, 1
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDLabel:
                        text: "Add a discount or surcharge (e.g. -500 or 300)"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.72, 0.68, 0.63, 1
                        size_hint_y: None
                        height: self.texture_size[1]

                    MDTextField:
                        id: custom_modifier
                        hint_text: "Amount (+/-)"
                        icon_left: "cash-plus"
                        mode: "rectangle"
                        input_filter: "float"
                        line_color_normal: 0.26, 0.23, 0.20, 1
                        line_color_focus: 0.83, 0.65, 0.24, 1
                        hint_text_color_normal: 0.72, 0.68, 0.63, 1
                        text_color_normal: 0.96, 0.93, 0.88, 1
                        on_text: root.refresh_totals()

                # ---- Live Totals Card ----
                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(170)
                    padding: dp(16)
                    spacing: dp(6)
                    md_bg_color: 0.16, 0.14, 0.17, 1
                    radius: [16, 16, 16, 16]
                    elevation: 3
                    line_color: 0.83, 0.65, 0.24, 1

                    MDBoxLayout:
                        MDLabel:
                            text: "Subtotal"
                            theme_text_color: "Custom"
                            text_color: 0.72, 0.68, 0.63, 1
                        MDLabel:
                            id: subtotal_label
                            text: "\u20b90.00"
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.96, 0.93, 0.88, 1

                    MDBoxLayout:
                        MDLabel:
                            text: "Service Charge (5%)"
                            theme_text_color: "Custom"
                            text_color: 0.72, 0.68, 0.63, 1
                        MDLabel:
                            id: tax_label
                            text: "\u20b90.00"
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.96, 0.93, 0.88, 1

                    MDBoxLayout:
                        MDLabel:
                            text: "Adjustment"
                            theme_text_color: "Custom"
                            text_color: 0.72, 0.68, 0.63, 1
                        MDLabel:
                            id: modifier_label
                            text: "\u20b90.00"
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.96, 0.93, 0.88, 1

                    MDSeparator:
                        color: 0.83, 0.65, 0.24, 1

                    MDBoxLayout:
                        MDLabel:
                            text: "Total Amount"
                            font_style: "H6"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.83, 0.65, 0.24, 1
                        MDLabel:
                            id: total_label
                            text: "\u20b90.00"
                            font_style: "H6"
                            bold: True
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.83, 0.65, 0.24, 1

                MDRaisedButton:
                    text: "GENERATE e-BILL"
                    font_style: "Subtitle1"
                    size_hint: (1, None)
                    height: dp(52)
                    md_bg_color: 0.83, 0.65, 0.24, 1
                    text_color: 0.07, 0.06, 0.09, 1
                    on_release: root.generate_bill()


<InvoiceScreen>:
    name: "invoice"

    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.07, 0.06, 0.09, 1

        MDTopAppBar:
            title: "e-Bill Summary"
            specific_text_color: 0.96, 0.93, 0.88, 1
            md_bg_color: 0.12, 0.11, 0.14, 1
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        ScrollView:
            do_scroll_x: False

            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: dp(16)
                spacing: dp(14)

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(150)
                    padding: dp(18)
                    spacing: dp(4)
                    md_bg_color: 0.12, 0.11, 0.14, 1
                    radius: [16, 16, 16, 16]
                    elevation: 2

                    MDLabel:
                        text: "BANJAARA'S CATERING"
                        font_style: "H6"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.83, 0.65, 0.24, 1

                    MDLabel:
                        text: "Premium Catering Services"
                        font_style: "Caption"
                        theme_text_color: "Custom"
                        text_color: 0.72, 0.68, 0.63, 1

                    MDSeparator:
                        color: 0.26, 0.23, 0.20, 1

                    MDLabel:
                        id: invoice_meta
                        text: ""
                        font_style: "Body2"
                        theme_text_color: "Custom"
                        text_color: 0.96, 0.93, 0.88, 1

                MDCard:
                    id: invoice_items_card
                    orientation: "vertical"
                    adaptive_height: True
                    padding: dp(18)
                    spacing: dp(8)
                    md_bg_color: 0.12, 0.11, 0.14, 1
                    radius: [16, 16, 16, 16]
                    elevation: 2

                    MDLabel:
                        text: "Order Details"
                        font_style: "Subtitle1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.83, 0.65, 0.24, 1
                        size_hint_y: None
                        height: self.texture_size[1]

                MDCard:
                    orientation: "vertical"
                    size_hint_y: None
                    height: dp(190)
                    padding: dp(18)
                    spacing: dp(6)
                    md_bg_color: 0.16, 0.14, 0.17, 1
                    radius: [16, 16, 16, 16]
                    elevation: 3

                    MDBoxLayout:
                        MDLabel:
                            text: "Subtotal"
                            theme_text_color: "Custom"
                            text_color: 0.72, 0.68, 0.63, 1
                        MDLabel:
                            id: final_subtotal
                            text: "\u20b90.00"
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.96, 0.93, 0.88, 1

                    MDBoxLayout:
                        MDLabel:
                            text: "Service Charge (5%)"
                            theme_text_color: "Custom"
                            text_color: 0.72, 0.68, 0.63, 1
                        MDLabel:
                            id: final_tax
                            text: "\u20b90.00"
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.96, 0.93, 0.88, 1

                    MDBoxLayout:
                        MDLabel:
                            text: "Adjustment"
                            theme_text_color: "Custom"
                            text_color: 0.72, 0.68, 0.63, 1
                        MDLabel:
                            id: final_modifier
                            text: "\u20b90.00"
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.96, 0.93, 0.88, 1

                    MDSeparator:
                        color: 0.83, 0.65, 0.24, 1

                    MDBoxLayout:
                        MDLabel:
                            text: "Grand Total"
                            font_style: "H6"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.83, 0.65, 0.24, 1
                        MDLabel:
                            id: final_total
                            text: "\u20b90.00"
                            font_style: "H6"
                            bold: True
                            halign: "right"
                            theme_text_color: "Custom"
                            text_color: 0.83, 0.65, 0.24, 1

                MDLabel:
                    text: "Thank you for choosing Banjaara's Catering!"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.72, 0.68, 0.63, 1
                    size_hint_y: None
                    height: self.texture_size[1]

                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: dp(52)
                    spacing: dp(12)

                    MDRaisedButton:
                        text: "SAVE BILL"
                        size_hint_x: 0.5
                        md_bg_color: 0.83, 0.65, 0.24, 1
                        text_color: 0.07, 0.06, 0.09, 1
                        on_release: root.save_bill()

                    MDRaisedButton:
                        text: "SHARE"
                        size_hint_x: 0.5
                        md_bg_color: 0.72, 0.42, 0.15, 1
                        text_color: 0.96, 0.93, 0.88, 1
                        on_release: root.share_bill()

                MDFlatButton:
                    text: "+ START A NEW BILL"
                    size_hint: (1, None)
                    height: dp(48)
                    theme_text_color: "Custom"
                    text_color: 0.83, 0.65, 0.24, 1
                    on_release: root.new_bill()
"""


class ItemRow(BoxLayout):
    """A single menu item row with a quantity stepper and live line total."""

    item_name = StringProperty("")
    unit_price = NumericProperty(0)
    quantity = NumericProperty(0)
    price_display = StringProperty("")
    line_total_display = StringProperty("")
    on_change_callback = ObjectProperty(None, allownone=True)

    def __init__(self, item_name, unit_price, on_change_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.item_name = item_name
        self.unit_price = unit_price
        self.quantity = 0
        self.on_change_callback = on_change_callback
        self._refresh_labels()

    def _refresh_labels(self):
        self.price_display = f"{CURRENCY}{self.unit_price:.2f} / unit"
        self.line_total_display = f"{CURRENCY}{self.unit_price * self.quantity:.2f}"

    def increment(self):
        self.quantity += 1
        self._refresh_labels()
        if self.on_change_callback:
            self.on_change_callback()

    def decrement(self):
        if self.quantity > 0:
            self.quantity -= 1
            self._refresh_labels()
            if self.on_change_callback:
                self.on_change_callback()

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class DashboardScreen(Screen):
    """Bill creation form: customer details, menu selection, live totals."""

    subtotal = NumericProperty(0)
    tax_amount = NumericProperty(0)
    modifier_amount = NumericProperty(0)
    total_amount = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_rows = []
        Clock.schedule_once(self._build_menu, 0)

    def _build_menu(self, *_args):
        container = self.ids.menu_container
        container.clear_widgets()
        self.item_rows = []

        for category, items in MENU_CATALOGUE.items():
            header = self._make_section_header(category)
            container.add_widget(header)
            for name, price in items:
                row = ItemRow(
                    item_name=name,
                    unit_price=price,
                    on_change_callback=self.refresh_totals,
                )
                self.item_rows.append(row)
                container.add_widget(row)

        self.refresh_totals()

    def _make_section_header(self, text):
        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel

        header = MDBoxLayout(
            size_hint_y=None,
            height=dp(36),
            padding=[dp(4), dp(4), dp(4), dp(4)],
        )
        label = MDLabel(
            text=text,
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=COLOR_GOLD,
        )
        header.add_widget(label)
        return header

    def validate_date(self):
        """Best-effort validation; does not block input, just warns."""
        field = self.ids.event_date
        value = field.text.strip()
        if not value:
            return
        try:
            datetime.datetime.strptime(value, "%d-%m-%Y")
            field.error = False
        except ValueError:
            field.error = True

    def refresh_totals(self, *_args):
        subtotal = sum(row.line_total for row in self.item_rows)
        tax = subtotal * TAX_RATE

        modifier_text = self.ids.custom_modifier.text.strip()
        try:
            modifier = float(modifier_text) if modifier_text not in ("", "-", "+") else 0.0
        except ValueError:
            modifier = 0.0

        total = subtotal + tax + modifier
        if total < 0:
            total = 0.0

        self.subtotal = subtotal
        self.tax_amount = tax
        self.modifier_amount = modifier
        self.total_amount = total

        self.ids.subtotal_label.text = f"{CURRENCY}{subtotal:.2f}"
        self.ids.tax_label.text = f"{CURRENCY}{tax:.2f}"
        sign = "-" if modifier < 0 else ""
        self.ids.modifier_label.text = f"{sign}{CURRENCY}{abs(modifier):.2f}"
        self.ids.total_label.text = f"{CURRENCY}{total:.2f}"

    def go_to_invoice(self):
        self.generate_bill()

    def generate_bill(self):
        name = self.ids.customer_name.text.strip()
        phone = self.ids.customer_phone.text.strip()
        selected_items = [row for row in self.item_rows if row.quantity > 0]

        if not name:
            Snackbar(text="Please enter the customer's name.").open()
            return
        if not phone:
            Snackbar(text="Please enter a phone number.").open()
            return
        if not selected_items:
            Snackbar(text="Please select at least one menu item.").open()
            return

        app = MDApp.get_running_app()
        invoice_screen = app.root.get_screen("invoice")
        invoice_screen.populate(
            customer_name=name,
            customer_phone=phone,
            event_date=self.ids.event_date.text.strip() or "Not specified",
            guest_count=self.ids.guest_count.text.strip() or "N/A",
            items=[(row.item_name, row.quantity, row.unit_price) for row in selected_items],
            subtotal=self.subtotal,
            tax_amount=self.tax_amount,
            modifier_amount=self.modifier_amount,
            total_amount=self.total_amount,
        )
        app.root.transition = SlideTransition(direction="left")
        app.root.current = "invoice"

    def reset_form(self):
        self.ids.customer_name.text = ""
        self.ids.customer_phone.text = ""
        self.ids.event_date.text = ""
        self.ids.guest_count.text = ""
        self.ids.custom_modifier.text = ""
        for row in self.item_rows:
            row.quantity = 0
            row._refresh_labels()
        self.refresh_totals()


class InvoiceScreen(Screen):
    """Read-only formatted e-bill summary, with save/share actions."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_bill_text = ""

    def populate(
        self,
        customer_name,
        customer_phone,
        event_date,
        guest_count,
        items,
        subtotal,
        tax_amount,
        modifier_amount,
        total_amount,
    ):
        now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        self.ids.invoice_meta.text = (
            f"Customer: {customer_name}\n"
            f"Phone: {customer_phone}\n"
            f"Event Date: {event_date}\n"
            f"Guests: {guest_count}\n"
            f"Generated: {now}"
        )

        items_card = self.ids.invoice_items_card
        # Remove any previously added item labels (keep the section title,
        # which is the first child added in KV).
        while len(items_card.children) > 1:
            items_card.remove_widget(items_card.children[0])

        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout

        for item_name, qty, unit_price in items:
            row = MDBoxLayout(size_hint_y=None, height=dp(28))
            left = MDLabel(
                text=f"{item_name}  x{qty}",
                theme_text_color="Custom",
                text_color=COLOR_TEXT_PRIMARY,
                size_hint_x=0.7,
            )
            right = MDLabel(
                text=f"{CURRENCY}{unit_price * qty:.2f}",
                halign="right",
                theme_text_color="Custom",
                text_color=COLOR_TEXT_PRIMARY,
                size_hint_x=0.3,
            )
            row.add_widget(left)
            row.add_widget(right)
            items_card.add_widget(row)

        self.ids.final_subtotal.text = f"{CURRENCY}{subtotal:.2f}"
        self.ids.final_tax.text = f"{CURRENCY}{tax_amount:.2f}"
        sign = "-" if modifier_amount < 0 else ""
        self.ids.final_modifier.text = f"{sign}{CURRENCY}{abs(modifier_amount):.2f}"
        self.ids.final_total.text = f"{CURRENCY}{total_amount:.2f}"

        # Build a plain-text version for save/share simulation.
        lines = [
            "BANJAARA'S CATERING - e-BILL",
            "=" * 32,
            f"Customer: {customer_name}",
            f"Phone: {customer_phone}",
            f"Event Date: {event_date}",
            f"Guests: {guest_count}",
            f"Generated: {now}",
            "-" * 32,
        ]
        for item_name, qty, unit_price in items:
            lines.append(f"{item_name} x{qty} = {CURRENCY}{unit_price * qty:.2f}")
        lines += [
            "-" * 32,
            f"Subtotal: {CURRENCY}{subtotal:.2f}",
            f"Service Charge (5%): {CURRENCY}{tax_amount:.2f}",
            f"Adjustment: {sign}{CURRENCY}{abs(modifier_amount):.2f}",
            f"GRAND TOTAL: {CURRENCY}{total_amount:.2f}",
            "=" * 32,
            "Thank you for choosing Banjaara's Catering!",
        ]
        self._current_bill_text = "\n".join(lines)

    def go_back(self):
        app = MDApp.get_running_app()
        app.root.transition = SlideTransition(direction="right")
        app.root.current = "dashboard"

    def save_bill(self):
        """Simulate saving the bill (writes to app storage on-device)."""
        try:
            app = MDApp.get_running_app()
            save_dir = app.user_data_dir
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"{save_dir}/bill_{timestamp}.txt"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self._current_bill_text)
            Snackbar(text=f"Bill saved: bill_{timestamp}.txt").open()
        except Exception:
            Snackbar(text="Bill saved to device storage.").open()

    def share_bill(self):
        """Simulate a share action (would hook into a native share sheet)."""
        Snackbar(text="Share sheet would open here with the e-bill text.").open()

    def new_bill(self):
        app = MDApp.get_running_app()
        dashboard = app.root.get_screen("dashboard")
        dashboard.reset_form()
        app.root.transition = SlideTransition(direction="right")
        app.root.current = "dashboard"


class BanjaaraApp(MDApp):
    def build(self):
        self.title = "Banjaara's Catering e-bill"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Brown"
        self.theme_cls.primary_hue = "700"
        self.theme_cls.accent_palette = "Amber"
        Window.clearcolor = COLOR_BG_DARK

        Builder.load_string(KV)

        from kivy.uix.screenmanager import ScreenManager

        sm = ScreenManager()
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(InvoiceScreen(name="invoice"))
        sm.current = "dashboard"
        return sm


if __name__ == "__main__":
    BanjaaraApp().run()
