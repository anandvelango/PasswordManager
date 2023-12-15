import psycopg2
import uuid
import getpass
import os
from tabulate import tabulate
from cryptography.fernet import Fernet

# connect to postgres db
def connect_db(db_password):
    conn = psycopg2.connect(host="localhost",
                            dbname="postgres",
                            user="postgres",
                            password=db_password,
                            port=5432) 

    return conn

# load key for encrypting/decrypting passwords (symmetric encryption)
def load_key():
    if os.path.exists("key.key"):
        with open("key.key", "rb") as f:
            key = f.read()
    else:
        with open("key.key", "wb") as f:
            key = Fernet.generate_key()
            f.write(key)

    return key

# add password
def add_password():
    username = str(input("Username/email: "))
    account = str(input("Account: "))
    password = str(input("Password: "))
    
    enc_password = fernet.encrypt(password.encode()).decode()
    insert_password = f"""
    INSERT INTO creds (id, username, account, password) VALUES
    ({uuid.uuid1().int>>110}, '{username}', '{account}', '{enc_password}')
    """
    
    cur.execute(insert_password)
    
    conn.commit()
    print("[+] Password added!")

# view password
def view_password():
    cur.execute("""SELECT id, username, account FROM creds""")
    table.clear()
    for row in cur.fetchall():
        table.append([row[0], row[1], row[2]])    
    print(tabulate(table, headers, tablefmt="outline"))
    
    if len(table) > 0:    
        password_id = int(input("\nEnter by ID which password you want to view: ").strip())
        cur.execute(f"""SELECT username, account, password FROM creds WHERE id = {password_id}""")
        row = cur.fetchone()
        
        if row is not None:
            print(f"\n{' | '.join(row[:2])}")
            print(f"Password: {fernet.decrypt(row[-1]).decode()}")
        else:
            print(f"[-] Invalid ID: {password_id}")
    else:
        print("There are no passwords at the moment. Enter '1' to start adding passwords.")
    
    conn.commit()
    
# delete password
def delete_password():
    cur.execute("""SELECT id, username, account FROM creds""")
    table.clear()
    for row in cur.fetchall():
        table.append([row[0], row[1], row[2]])    
    print(tabulate(table, headers, tablefmt="outline"))
    if len(table) > 0:    
        password_id = int(input("\nEnter by ID which password you want to delete: ").strip())
        cur.execute(f"""SELECT * FROM creds WHERE id = {password_id}""")
        
        if cur.fetchone() is not None:
            cur.execute(f"""DELETE FROM creds WHERE id = {password_id}""")
            print("[+] Password deleted!")
        else:
            print(f"[!] Invalid ID: {password_id}")
    else:
        print("There are no passwords at the moment.")
    
    conn.commit()

# update password
def update_password():
    cur.execute("""SELECT id, username, account FROM creds""")
    table.clear()
    for row in cur.fetchall():
        table.append([row[0], row[1], row[2]])    
    print(tabulate(table, headers, tablefmt="outline"))
    
    if len(table) > 0:    
        password_id = int(input("Enter by ID which password/username you want to update: ").strip())
        cur.execute(f"""SELECT * FROM creds WHERE id = {password_id}""")
        
        if cur.fetchone() is not None:
            update_username = input("Update username?(y/n): ")
            if update_username == "y":
                updated_username = input("Enter new username: ")
                update_passwd = input("Update password?(y/n): ")
                if update_passwd == "y":
                    updated_password = input("Enter new password: ")
                    cur.execute(f"""UPDATE creds SET username = '{updated_username}', password = '{fernet.encrypt(updated_password.encode()).decode()}' WHERE id = {password_id}""")
                    print("[+] Password updated!")
                elif update_passwd == "n":
                    cur.execute(f"""UPDATE creds SET username = '{updated_username}' WHERE id = {password_id}""")
                    print("[+] Password updated!")
            elif update_username == "n":
                update_passwd = input("Update password?(y/n): ")
                if update_passwd == "y":
                    updated_password = input("Enter new password: ")
                    cur.execute(f"""UPDATE creds SET password = '{fernet.encrypt(updated_password.encode()).decode()}' WHERE id = {password_id}""")
                    print("[+] Password updated!")
                elif update_passwd == "n":
                    pass
        else:
            print(f"[!] Invalid ID: {password_id}")      
    else:
        print("There are no passwords at the moment.")
    
    conn.commit()

# main func for selecting options
def main(banner):
    cur.execute("""CREATE TABLE IF NOT EXISTS creds(
        id INT PRIMARY KEY,
        username VARCHAR(255),
        account VARCHAR(255),
        password VARCHAR(255)
    );
    """)
    
    print(banner)
    
    conn.commit()
    
    try:
        while True:
            choice = input("[>>>] ").lower().strip()
            if choice == "1":
                add_password()
            elif choice == "2":
                view_password()
            elif choice == "3":
                delete_password()
            elif choice == "4":
                update_password()
            elif choice == "h" or choice == "help":
                print(banner)
            elif choice == "clear" or choice == "cls":
                os.system("cls" if os.name == "nt" else "clear")
            elif choice == "q" or choice == "exit":
                print("[!] Exited the program")
                cur.close()
                conn.close()
                exit()
            else:
                print("[!] Not a valid input")
    except KeyboardInterrupt:
        print("\n[-] Exited the program with keyboard")
        exit()
            
if __name__ == "__main__":    
    # authenticate user and password
    db_password = getpass.getpass("[+] Postgres DB password: ")
    try:
        conn = connect_db(db_password)
        cur = conn.cursor()
        print("[+] User authenticated!")
    except psycopg2.OperationalError as e:
        print("[!] Failed to connect to database: Incorrect password")
        exit()
    
    key = load_key()
    fernet = Fernet(key)
    
    headers = ["id", "username", "account"]
    table = [] 
    
    # banner
    banner = ("""
    
            :+++++++:        Password Manager
           #=       =*       Coded by @anandvelango
          *=         ++      ================
          %.         :#      
        -=@++++++++++*%=-    [1] Add password
      .%-               :#.  [2] View passsword
      =*                 +=  [3] Delete password
      =*       %@#       +=  [4] Update password
      =*       =@=       +=  
      =*       :@:       +=  [h] Help
      =*                 +=  [q] Exit
      .%:               :%.
          """)
    
    main(banner)
    cur.close()
    conn.close()