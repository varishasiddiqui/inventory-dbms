
import firebase_admin
from firebase_admin import credentials, firestore,initialize_app
from datetime import datetime
# Path to your service account key (downloaded from Firebase Console)
cred = credentials.Certificate(r'E:\Downloads\inventory-13961-firebase-adminsdk-fbsvc-bb3457ef2f.json')

initialize_app(cred)

db = firestore.client()

print('firebase connected successfully')
 
def add_employee_to_firestore(id, name, dob, contact, email, designation, department, work_shift, doj, salary, address, status, gender, education, nationality, emptype, user_type, password):
    """Insert a new student into the 'students' collection."""
    doc_ref = db.collection('employee_details').document(str(id))
    doc_ref.set({
            'empID': id,
            'empName': name,
            'empDob': dob,
            'empContact': contact,
            'empEmail': email,
            'empDesig': designation,
            'empDep': department,
            'empWork_shift': work_shift,
            'empDoj': doj,
            'empSalary': salary,
            'empAddress': address,
            'empStatus': status,
            'empGender': gender,
            'empEducation': education,
            'empNationality': nationality,
            'empType': emptype,
            'empUser_type': user_type,
            'empPassword': password
    })
    print('Employee added successfully in firebase')

def add_category_to_firestore(id,name,description):
    doc_ref = db.collection('category').document(str(id))
    doc_ref.set({
        'catID': id,
        'catName': name,
        'catDescription': description
        })
    print('Category added successfully in firebase')

def add_product_to_firestore(name, category, supplier, price, quantity, status):
    try:
        # Get the highest current product ID from Firestore (or use a predefined range)
        product_ref = db.collection('product').order_by('prodID', direction=firestore.Query.DESCENDING).limit(1)
        query_result = product_ref.stream()
        
        # Check if there are any products
        max_prod_id = 0
        for doc in query_result:
            product_data = doc.to_dict()
            max_prod_id = product_data.get('prodID', 0)
        
        # Generate the new product ID (incrementing from the highest existing ID)
        new_prod_id = max_prod_id + 1
        
        # Create product data with the new ID
        doc_ref = db.collection('product').document(str(new_prod_id))  # Using custom ID
        doc_ref.set({
            'prodID': new_prod_id,
            'prodName': name,
            'prodCategory': category,
            'prodSupplier': supplier,
            'prodPrice': price,
            'prodQuantity': quantity,
            'prodStatus': status
        })
        print(f'Product added successfully in Firebase with ID: {new_prod_id}')
        return new_prod_id  # Return the generated ID
    except Exception as e:
        print(f"Error adding product to Firestore: {e}")
        return None

def add_supplier_to_firebase(invoiceNo,name,contact,email,address,description):
    doc_ref = db.collection('supplier').document(str(invoiceNo))
    doc_ref.set({
        'invNo': invoiceNo,
        'invName': name,
        'invContact': contact,
        'invEmail': email,
        'invAddress': address,
        'invDescription': description
        })
    print('Supplier added to firestore successfully')
def tax_in_firebase(tax_value):
    try:
        # Reference to the 'tax' document (you can use a specific document name like 'tax_settings')
        tax_ref = db.collection('tax').document('tax_value')  # or any specific document name
        # Set the tax value, using merge=True to overwrite the existing value
        tax_ref.set({
            'taxValue': tax_value
        }, merge=True)  # merge=True ensures that only 'taxValue' is updated, other fields remain unchanged
        
        print(f'Tax value updated successfully to {tax_value}')
    except Exception as e:
        print(f"Error updating tax value in Firestore: {e}")

def update_employee_in_firestore(employee_id, updated_data):
    try:
        # Reference to the employee document in Firestore using the employee ID
        employee_ref = db.collection('employee_details').document(str(employee_id))
        
        # Check if the current data is different from the new data
        doc = employee_ref.get()
        current_data = doc.to_dict() if doc.exists else None

        if current_data == updated_data:
            print("Nothing to update, employee data is identical.")
            return

        # Update the employee's details in Firestore
        employee_ref.update(updated_data)
        
        print(f"Employee with ID {employee_id} updated successfully.")
    except Exception as e:
        print(f"Error updating employee in Firestore: {e}")
def delete_employee_from_firestore(id):
    try:
        # Reference to the employee document in Firestore using the employee ID
        employee_ref = db.collection('employee_details').document(str(id))

        # Fetch the current data before deletion (for backup)
        doc = employee_ref.get()

        # Check if the document exists
        if not doc.exists:
            print(f"No employee found with ID {id}.")
            return

        # Retrieve the data to be inserted into the 'employee_del' collection
        deleted_data = doc.to_dict()

        # Insert the deleted employee data into 'employee_del' collection
        db.collection('employee_del').document(str(id)).set(deleted_data)

        # Delete the employee document from 'employee_details'
        employee_ref.delete()

        print(f"Employee with ID {id} has been deleted and backed up successfully.")
        
    except Exception as e:
        print(f"Error deleting employee from Firestore: {e}")
