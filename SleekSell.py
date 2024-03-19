import json
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, messagebox
import hashlib

class Product:
    def __init__(self, product_id, name, price, quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, product):
        if product.product_id in self.products:
            self.products[product.product_id].quantity += product.quantity
        else:
            self.products[product.product_id] = product

    def remove_product(self, product_id, quantity):
        if product_id in self.products:
            if self.products[product_id].quantity >= quantity:
                self.products[product_id].quantity -= quantity
            else:
                print("Insufficient quantity in inventory.")
        else:
            print("Product not found in inventory.")

class ShoppingCart:
    def __init__(self):
        self.items = []

    def add_item(self, product, quantity):
        self.items.append((product, quantity))

    def remove_item(self, product_id):
        for item in self.items:
            if item[0].product_id == product_id:
                self.items.remove(item)
                break
        else:
            print("Item not found in cart.")

    def calculate_total(self):
        total = sum(item[0].price * item[1] for item in self.items)
        return total

class Transaction:
    def __init__(self, transaction_id, items, total_amount, timestamp):
        self.transaction_id = transaction_id
        self.items = items
        self.total_amount = total_amount
        self.timestamp = timestamp

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

class UserManager:
    def __init__(self):
        self.users = {}

    def add_user(self, user):
        hashed_password = self._hash_password(user.password)
        user.password = hashed_password
        self.users[user.username] = user

    def authenticate(self, username, password):
        if username in self.users:
            hashed_password = self._hash_password(password)
            if self.users[username].password == hashed_password:
                return True
        return False

    def _hash_password(self, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return hashed_password

class POS:
    def __init__(self):
        self.inventory = Inventory()
        self.shopping_cart = ShoppingCart()
        self.transactions = []
        self.user_manager = UserManager()
        self.current_user = None

    def load_inventory(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            for item in data:
                product = Product(item['product_id'], item['name'], item['price'], item['quantity'])
                self.inventory.add_product(product)

    def save_inventory(self, file_path):
        data = [{'product_id': product.product_id, 'name': product.name, 'price': product.price, 'quantity': product.quantity} for product in self.inventory.products.values()]
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    def add_to_cart(self, product_id, quantity):
        if product_id in self.inventory.products:
            product = self.inventory.products[product_id]
            if product.quantity >= quantity:
                self.shopping_cart.add_item(product, quantity)
                self.inventory.remove_product(product_id, quantity)
                print(f"{quantity} {product.name}(s) added to the cart.")
            else:
                print("Insufficient quantity in inventory.")
        else:
            print("Product not found in inventory.")

    def remove_from_cart(self, product_id):
        self.shopping_cart.remove_item(product_id)
        product = self.inventory.products[product_id]
        self.inventory.add_product(product)

    def checkout(self):
        if not self.shopping_cart.items:
            print("The shopping cart is empty.")
            return

        total_amount = self.shopping_cart.calculate_total()
        transaction_id = len(self.transactions) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transaction = Transaction(transaction_id, self.shopping_cart.items, total_amount, timestamp)
        self.transactions.append(transaction)

        print("===== Receipt =====")
        for product, quantity in self.shopping_cart.items:
            print(f"{product.name} - Quantity: {quantity} - Price: ${product.price * quantity}")
        print(f"Total amount: ${total_amount}")
        print(f"Transaction ID: {transaction_id}")
        print(f"Timestamp: {timestamp}")
        print("===================")

        self.shopping_cart.items = []

        # Update inventory after checkout
        self.save_inventory('inventory.json')

class Localization:
    def __init__(self, language):
        self.language = language
        self.translations = {
            "en": {
                "product_id": "Product ID:",
                "quantity": "Quantity:",
                "add_to_cart": "Add to Cart",
                "checkout": "Checkout",
                "checkout_success": "Checkout completed successfully."
            },
            "fr": {
                "product_id": "Identifiant du produit :",
                "quantity": "Quantité :",
                "add_to_cart": "Ajouter au panier",
                "checkout": "Check-out",
                "checkout_success": "Check-out complété avec succès."
            }
        }

    def translate(self, key):
        return self.translations.get(self.language, {}).get(key, key)

class POS_GUI:
    def __init__(self, pos, localization):
        self.pos = pos
        self.localization = localization
        self.root = Tk()
        self.root.title("SleekSell POS")

        # Set window size and position
        window_width = 800
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Define labels and entry fields
        self.label_product_id = Label(self.root, text=self.localization.translate("product_id"))
        self.label_product_id.grid(row=0, column=0, padx=10, pady=10)
        self.entry_product_id = Entry(self.root)
        self.entry_product_id.grid(row=0, column=1, padx=10, pady=10)

        self.label_quantity = Label(self.root, text=self.localization.translate("quantity"))
        self.label_quantity.grid(row=1, column=0, padx=10, pady=10)
        self.entry_quantity = Entry(self.root)
        self.entry_quantity.grid(row=1, column=1, padx=10, pady=10)

        # Define buttons
        self.button_add_to_cart = Button(self.root, text=self.localization.translate("add_to_cart"), command=self.add_to_cart)
        self.button_add_to_cart.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.button_checkout = Button(self.root, text=self.localization.translate("checkout"), command=self.checkout)
        self.button_checkout.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.button_view_inventory = Button(self.root, text="View Inventory", command=self.view_inventory)
        self.button_view_inventory.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.button_view_receipt = Button(self.root, text="View Receipt", command=self.view_receipt)
        self.button_view_receipt.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Developed by label
        self.label_developed_by = Label(self.root, text="Developed by Script Maker", font=("Arial", 10, "bold"))
        self.label_developed_by.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    def add_to_cart(self):
        product_id = self.entry_product_id.get()
        quantity = int(self.entry_quantity.get())
        self.pos.add_to_cart(product_id, quantity)
        self.entry_product_id.delete(0, 'end')
        self.entry_quantity.delete(0, 'end')

    def checkout(self):
        self.pos.checkout()
        messagebox.showinfo("Checkout", self.localization.translate("checkout_success"))

    def view_inventory(self):
        inventory_text = "Inventory:\n"
        for product in self.pos.inventory.products.values():
            inventory_text += f"{product.name} - Price: ${product.price} - Quantity: {product.quantity}\n"
        messagebox.showinfo("Inventory", inventory_text)

    def view_receipt(self):
        if self.pos.transactions:
            latest_transaction = self.pos.transactions[-1]
            receipt_text = "===== Receipt =====\n"
            for product, quantity in latest_transaction.items:
                receipt_text += f"{product.name} - Quantity: {quantity} - Price: ${product.price * quantity}\n"
            receipt_text += f"Total amount: ${latest_transaction.total_amount}\n"
            receipt_text += f"Transaction ID: {latest_transaction.transaction_id}\n"
            receipt_text += f"Timestamp: {latest_transaction.timestamp}\n"
            receipt_text += "===================\n"
            messagebox.showinfo("Receipt", receipt_text)
        else:
            messagebox.showinfo("Receipt", "No transactions yet.")

    def run(self):
        self.root.mainloop()

# Sample usage:
pos = POS()
pos.user_manager.add_user(User("admin", "admin123", "admin"))
pos.user_manager.add_user(User("cashier", "cashier123", "cashier"))
pos.load_inventory('inventory.json')
pos.user_manager.authenticate("admin", "admin123")
localization = Localization("en")
pos_gui = POS_GUI(pos, localization)
pos_gui.run()
