from utils import *
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from testcases.rhsm.rhsmguilocator import RHSMGuiLocator
from testcases.rhsm.rhsmconstants import RHSMConstants
from utils.exception.failexception import FailException

class tc_ID190637_GUI_open_subscription_manager_about_from_menu(RHSMGuiBase):

    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % self.__class__.__name__)
        try:
            try:
                self.open_subscription_manager()
                self.click_about_menu()
                #for 7.1 uncomment the following line:
                #if self.check_object_exist("about-subscription-manager-dialog", "about-subscription-manager-dialog"):
                if self.check_object_exist("about-subscription-manager-dialog", "about-subscription-manager-dialog"):
                    logger.info("It's successful to check open_subscription_manager_about_from_menu.")
                else:
                    raise FailException("Test Faild - Failed to check open_subscription_manager_about_from_menu!")
                self.assert_(True, case_name)
            except Exception, e:
                logger.error("Test Failed - ERROR Message:" + str(e))
                self.assert_(False, case_name)
        finally:
            self.capture_image(case_name)
            self.close_window("about-subscription-manager-dialog")
            self.restore_gui_environment()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()