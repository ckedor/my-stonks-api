import sys


def main():
    if len(sys.argv) < 2:
        print("⚠️  Comando ausente. Use: `python manage.py create_superuser`")
        return

    command = sys.argv[1]

    if command == "create_superuser":
        from app.modules.users.scripts import create_superuser

        create_superuser.run()

    else:
        print(f"❌ Comando desconhecido: {command}")


if __name__ == "__main__":
    main()
