import cmd
import calendar


class Calend(cmd.Cmd):
    prompt = ">>> "

    def do_prmonth(self, args):
        "prints month"
        year, month = map(int, args.split())
        calendar.TextCalendar().prmonth(year, month)

    def do_pryear(self, year):
        "prints year"
        print(calendar.TextCalendar().pryear(int(year)))

    def complete_prmonth(self, text, line, begidx, endidx):
        return [m for m in self.Month if m.startswith(text)]

    def do_EOF(self, args):
        return 1


if __name__ == "__main__":
    Calend().cmdloop()
