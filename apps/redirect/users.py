class User:

    def __init__(self, id_, is_active: bool, is_anonymous: bool, is_authenticated: bool):
        self.id = id_
        self.is_active = is_active
        self.is_anonymous = is_anonymous
        self.is_authenticated = is_authenticated

    def get_id(self):
        return self.id


class AdminUser(User):

    def __init__(self):
        super().__init__(0, True, False, True)


class DefaultUser(User):

    def __init__(self):
        super().__init__(1, False, True, False)
