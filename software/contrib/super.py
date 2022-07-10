
class grampa():
    def __init__(self, name,lastname):
        self.name = name
        self.lastname = lastname
    def func_(self):
        print("grampa")
    def print_name(self):
        print(self.name + " " + self.lastname)
    def print_lastname(self):
        print(self.lastname)
    def print_firstname(self):
        print(self.name)
    def g_func(self):
        print("g_func")

class parent(grampa):
    
    def __init__(self, name,lastname,age):
        super().__init__(name,lastname)
        self.age = age
    def func_(self):
        print("parent")
    def print_age(self):
        print(self.age)
    def print_name(self):
        print(self.name + " " + self.lastname)
    def print_lastname(self):
        print(self.lastname)
    def print_firstname(self):
        print(self.name)

class son():
    def __init__(self, name,lastname,age,school):
        # parent.__init__(self,name,lastname,age)
        self.__parent = parent(name,lastname,age)

        self.school = school
    def func_(self):
        print("son")
    def print_school(self):
        print(self.school)
    def print_name(self):
        print("self.name + " " + self.lastname")
    def print_lastname(self):
        print(self.lastname)
    def print_firstname(self):
        print(self.name)

j = grampa('joaq','glz')
l = parent('luis','glz',66)
la = son('lui','glz',33,'axs')