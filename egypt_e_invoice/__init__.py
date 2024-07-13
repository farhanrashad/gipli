from . import models
from odoo.exceptions import UserError, ValidationError



def pre_init_hook(cr):
    try:
        import chilkat
        glob = chilkat.CkGlobal()
        success = glob.UnlockBundle("SEWRDN.CB1112022_ivwYuypT8625")
        if (success != True):
            print(glob.lastErrorText())
            exit(glob.lastErrorText())

        status = glob.get_UnlockStatus()
        if (status == 2):
            print("Unlocked using purchased unlock code.")
        else:
            print("Unlocked in trial mode.")

        # The LastErrorText can be examined in the success case to see if it was unlocked in
        # trial more, or with a purchased unlock code.
        print(glob.lastErrorText())
    except ImportError:
        pass
