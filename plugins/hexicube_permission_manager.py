import json
from base_plugin import BasePlugin

class PermissionManagerPlugin(BasePlugin):
    name = "permission_manager"

    def activate(self):
        self.can_save = False
        super(PermissionManagerPlugin, self).activate()
        try:
            with open("core_plugins/permission_manager/groups.json") as f:
                self.groups = json.load(f)
            self.can_save = True
        except:
            self.groups = []
            self.creategroup("RESTRICTED")
            self.creategroup("GUEST")
            self.addgroupperm("GUEST", "chat")
            self.creategroup("REGISTERED")
            self.setgroupparent("REGISTERED", "GUEST")
            self.addgroupperm("REGISTERED", "build")
            self.addgroupperm("REGISTERED", "interact")
            self.creategroup("MODERATOR")
            self.setgroupparent("MODERATOR", "REGISTERED")
            self.creategroup("ADMIN")
            self.setgroupparent("ADMIN", "MODERATOR")
            self.creategroup("OWNER")
            self.setgroupparent("OWNER", "ADMIN")
            self.addgroupperm("OWNER", "*")
            self.can_save = True
            self.players = []
            self.save()
        try:
            with open("core_plugins/permission_manager/players.json") as f:
                self.players = json.load(f)
        except:
            self.players = []
    
    def after_connect_response(self, data):
        player = self.protocol.player.uuid
        if not self.getplayergroups(player):
            playerdata = [player, []]
            self.players.append(playerdata)
            self.addtogroup(player, "GUEST")
            """TODO: owner check"""
    
    def playerhasperm(self, player, permission):
        groups = self.getplayergroups(player)
        for group in groups:
            if self.grouphasperm(group, permission):
                return True
        return False
    
    def grouphasperm(self, group, permission):
        group = self.getgroup(group)
        if group:
            for perm in group[2]:
                if perm == permission:
                    return True
                if perm == "*":
                    return True
            if group[1] != "":
                return self.grouphasperm(group[1], permission)
        return False
    
    def creategroup(self, group):
        othergroup = self.getgroup(group)
        if othergroup:
            return False
        group = [group, "", []]
        self.groups.append(group)
        self.save()
        return True
    
    def removegroup(self, group):
        group = self.getgroup(group)
        if group:
            self.groups.remove(group)
            self.save()
            return True
        return False
    
    def getgroup(self, group):
        for g in self.groups:
            if g[0] == group:
                return g
        return False
    
    def setgroupparent(self, group, parent):
        group = self.getgroup(group)
        if group:
            group[1] = parent
            self.save()
            return True
        return False
    
    def addgroupperm(self, group, permission):
        group = self.getgroup(group)
        if group:
            for perm in group[2]:
                if perm == permission:
                    return False
            group[2].append(permission)
            self.save()
            return True
        return False
    
    def delgroupperm(self, group, permission):
        group = self.getgroup(group)
        if group:
            for perm in group[2]:
                if perm == permission:
                    group[2].remove(permission)
                    self.save()
                    return True
            return False
        return False
    
    def getplayergroups(self, player):
        for p in self.players:
            if p[0] == player:
                return p[1]
        return False
    
    def addtogroup(self, player, group):
        for p in self.players:
            if p[0] == player:
                for g in p[1]:
                    if g == group:
                        return False
                p[1].append(group)
                self.save()
                return True
        return False
    
    def removefromgroup(self, player, group):
        for p in self.players:
            if p[0] == player:
                for g in p[1]:
                    if g == group:
                        p[1].remove(group)
                        self.save()
                        return True
                return False
        return False

    def save(self):
        if self.can_save:
            try:
                with open("core_plugins/permission_manager/groups.json", "w") as f:
                    json.dump(self.groups, f)
            except:
                self.logger.exception("Couldn't save groups.", exc_info=True)
                raise
            try:
                with open("core_plugins/permission_manager/players.json", "w") as f:
                    json.dump(self.players, f)
            except:
                self.logger.exception("Couldn't save players.", exc_info=True)
                raise

def perm(perm=""):
    def wrapper(func):
        func.perm = perm
        @wraps(func)
        def wrapped_function(self, *args, **kwargs):
            if self.playerhasperm(self.protocol.player.uuid, perm):
                return func(self, *args, **kwargs)
            else:
                self.protocol.send_chat_message("You don't have permission to do that.")
                return False
        return wrapped_function
    return wrapper