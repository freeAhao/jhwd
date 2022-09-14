from model.Settings import Settings


class Weapon():

    weapon_name = None
    scope = None
    a1 = None
    a2 = None
    a3 = None
    a4 = None

    def get_file_name(self,path):
        return path.split("/")[-1].split(".")[0].split("_")[0]

    def set_weapon_img_path(self,weaponpath):
        self.weapon_name = self.get_file_name(weaponpath)
    
    def set_attachment(self,index,attachmentpath):

        if attachmentpath == None:
            result = 0
        else:
            result = self.get_file_name(attachmentpath)

        if index==0 and self.scope != result:
            if result == 0 and self.scope == 1:
                return False
            result = 1 if result == 0 else result
            self.scope = result
            return True
        if index==1 and self.a1 != result:
            if result == 0 and self.a1 == 4:
                return False
            result = 4 if result == 0 else result
            self.a1 = result
            return True
        if index==2 and self.a2 != result:
            if result == 0 and self.a2 == 7:
                return False
            result = 7 if result == 0 else result
            self.a2 = result
            return True
        if index==3 and self.a3 != result:
            if result == 0 and self.a3 == 4:
                return False
            result = 4 if result == 0 else result
            self.a3 = result
            return True
        if index==4 and self.a4 != result:
            if result == 0 and self.a4 == 2:
                return False
            result = 2 if result == 0 else result
            self.a4 = result
            return True
        return False


    def get_weapon_img_path(self):
        if self.weapon_name:
            return Settings().resource_dir+"gun/{}.png".format(self.weapon_name)
        return Settings().resource_dir+"weapon_null.png"

    def get_scope_img_path(self):
        if self.scope and self.scope != 0:
            return  Settings().resource_dir+"attachments/1/{}.png".format(self.scope)
        return      Settings().resource_dir+"attachments/null.png"

    def get_a1_img_path(self):
        if self.a1 and self.scope != 0:
            return  Settings().resource_dir+"attachments/2/{}.png".format(self.a1)
        return      Settings().resource_dir+"attachments/null.png"

    def get_a2_img_path(self):
        if self.a2 and self.a2 != 0:
            return  Settings().resource_dir+"attachments/3/{}.png".format(self.a2)
        return      Settings().resource_dir+"attachments/null.png"

    def get_a3_img_path(self):
        if self.a3 and self.a3 != 0:
            return  Settings().resource_dir+"attachments/4/{}.png".format(self.a3)
        return      Settings().resource_dir+"attachments/null.png"

    def get_a4_img_path(self):
        if self.a4 and self.a4 != 0:
            return  Settings().resource_dir+"attachments/5/{}.png".format(self.a4)
        return      Settings().resource_dir+"attachments/null.png"