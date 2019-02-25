from collections import namedtuple

import npyscreen as npys
from pyfiglet import figlet_format


class SwitchFormButton(npys.ButtonPress):
    def __init__(self, *args, **kwargs):
        form = kwargs['form'] if 'form' in kwargs else None
        self.form = form

        npys.ButtonPress.__init__(self, *args, **kwargs)

    def whenPressed(self):
        self.parent.parentApp.switchForm(self.form)


class MyFormWithMenus(npys.FormWithMenus):
    def switchForms(self, *args):
        form = args[0] if args else None
        self.parentApp.switchForm(form)

    def create(self):

        self.menu = self.new_menu(name="Menu")
        self.menu.addItem(text='Ficha Servo',
                          onSelect=self.switchForms, arguments=['FichaServo'])
        self.menu.addItem(text='Demanda',
                          onSelect=self.switchForms, arguments={'form': ['Demanda']})
        self.menu.addItem(text='Sol. Parcial/Indisp.',
                          onSelect=self.switchForms, arguments={'form': ['PartialSol']})
        self.menu.addItem(text='Solver Options',
                          onSelect=self.switchForms, arguments={'form': ['Options']})
        self.menu.addItem(text='Exit', onSelect=self.switchForms,
                          arguments=None)


class TitleForm(MyFormWithMenus):
    def create(self):
        super().create()
        # I would much rather use a multi-line text widget, but the <Pager>
        # class doesn't seem to work to me. This is a dreadful workaround.
        title_lines = str(figlet_format(32 * ' ' + '- SAPI -', font='big')).splitlines() + \
            str(figlet_format(31 * ' ' + 'Scheduler', font='big')).splitlines()
        self.title_refs = []
        for line in title_lines:
            self.title_refs.append(
                self.add(npys.FixedText, value=line, editable=False))
        # Buttons
        self.start = self.add(
            SwitchFormButton, name="Start", relx=52, rely=-10, form='FichaServo')

        self.copyright = self.add(
            npys.FixedText, value='Rafael Eller 2019', editable=False, relx=48, rely=-3)
    # def buttonPress(self, widget):
    #     npys.notify_confirm(
    #         "BUTTON PRESSED!", title="Woot!", wrap=True, wide=True, editw=1)
    #     self.parentApp.switchForm('FichaServo')


class FichaServoForm(MyFormWithMenus):
    def create(self):
        super().create()
        self.add(npys.TitleFilenameCombo, name='Ficha Servo File:',
                 values=['tois', 'maluco'])

        # MENUS

        # Buttons
        # self.start = self.add(
        # SwitchFormButton, name="Start", relx=52, rely=-10, form='FichaServo')


# class FichaServoForm(npys.FormWithMenus):
#     def afterEditing(self):
#         self.parentApp.setNextForm(None)

#     def create(self):
#         self.myName = self.add(npys.TitleText, name='Name')
#         self.myDepartment = self.add(npys.TitleSelectOne, scroll_exit=True, max_height=3, name='Department', values=[
#             'Department 1', 'Department 2', 'Department 3'])
#         self.myDate = self.add(
#             npys.TitleDateCombo, name='Date Employed')


class MyApplication(npys.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', TitleForm, name='SAPI Scheduler')
        self.addForm('FichaServo', FichaServoForm, name='FichaServo')

        self.ficha_servo_path = None
        self.demanda_path = None
        self.partial_sol_path = None


if __name__ == '__main__':
    TestApp = MyApplication().run()
    print("All objects, baby.")
