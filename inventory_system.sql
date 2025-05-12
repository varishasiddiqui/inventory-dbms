-- Create the database
CREATE DATABASE IF NOT EXISTS inventory_dbms;
USE inventory_dbms;

-- Table: category_details
CREATE TABLE IF NOT EXISTS category_details (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100),
    category_des TEXT
);

-- Table: employee_del (backup or log table)
CREATE TABLE IF NOT EXISTS employee_del (
    empId INT PRIMARY KEY AUTO_INCREMENT,
    empName VARCHAR(100),
    empDob VARCHAR(30),
    empContact VARCHAR(50),
    empEmail VARCHAR(100),
    empDesig VARCHAR(50),
    empDep VARCHAR(50),
    empWork_shift VARCHAR(30),
    empDoj VARCHAR(100),
    empSalary VARCHAR(30),
    empAddress VARCHAR(100),
    empStatus VARCHAR(20),
    empGender VARCHAR(10),
    empEducation VARCHAR(50),
    empNationality VARCHAR(50),
    empType VARCHAR(50),
    empUser_type VARCHAR(50),
    empPassword VARCHAR(255)
);

-- Table: employee_details
CREATE TABLE IF NOT EXISTS employee_details (
    empId INT PRIMARY KEY AUTO_INCREMENT,
    empName VARCHAR(100),
    empDob VARCHAR(30),
    empContact VARCHAR(50),
    empEmail VARCHAR(100),
    empDesig VARCHAR(50),
    empDep VARCHAR(50),
    empWork_shift VARCHAR(30),
    empDoj VARCHAR(100),
    empSalary VARCHAR(30),
    empAddress VARCHAR(100),
    empStatus VARCHAR(20),
    empGender VARCHAR(10),
    empEducation VARCHAR(50),
    empNationality VARCHAR(50),
    empType VARCHAR(50),
    empUser_type VARCHAR(50),
    empPassword VARCHAR(255)
);

-- Table: product_details
CREATE TABLE IF NOT EXISTS product_details (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100),
    category VARCHAR(100),
    supplier VARCHAR(100),
    price DECIMAL(10,2),
    quantity INT,
    status VARCHAR(50)
);

-- Table: sales_data
CREATE TABLE IF NOT EXISTS sales_data (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    bill_no VARCHAR(50),
    product_id VARCHAR(20),
    product_name VARCHAR(100),
    quantity INT,
    unit_price DECIMAL(10,2),
    discount_percent DECIMAL(5,2),
    discount_amount DECIMAL(10,2),
    tax_percent DECIMAL(5,2),
    tax_amount DECIMAL(10,2),
    total_price DECIMAL(10,2),
    customer_name VARCHAR(100),
    contact VARCHAR(20),
    payment_mode VARCHAR(50),
    emp_name VARCHAR(100),
    sale_date DATE
);

-- Table: supplier_details
CREATE TABLE IF NOT EXISTS supplier_details (
    invoiceNo INT PRIMARY KEY,
    suppName VARCHAR(100),
    suppContact BIGINT,
    suppEmail VARCHAR(50),
    suppAddress VARCHAR(100),
    suppDes TEXT
);

-- Table: tax_data
CREATE TABLE IF NOT EXISTS tax_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tax DECIMAL(5,2)
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activity_type VARCHAR(50),
    reference_id INT,
    activity_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
