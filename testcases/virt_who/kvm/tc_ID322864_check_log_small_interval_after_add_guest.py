from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID322864_check_log_small_interval_after_add_guest(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("KVM_GUEST_NAME")
            guestuuid = self.vw_get_uuid(guest_name)

            rhsmlogpath='/var/log/rhsm/rhsm.log'

            #config the virt-who config file, set VIRTWHO_INTERVAL = 5
            cmd = "sed -i 's/.*VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=1/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(logger, cmd, "changing interval to 100s in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=1.")
            else:
                raise FailException("Failed to set VIRTWHO_INTERVAL=1.")
            #.restart virtwho service
            self.vw_restart_virtwho_new()
            #undefine a guest    
            self.vw_undefine_guest(guest_name)
            #define a guest
            self.vw_define_guest(guest_name)
            guestuuid = self.vw_get_uuid(guest_name)
            #check virt-who log
            cmd = "tail -50 %s " % rhsmlogpath
            ret, output = self.runcmd(logger, cmd, "check output in rhsm.log")
            if ret == 0 and ("AttributeError" not in output) and ("propSet" not in output) :
                logger.info("Success to check virt-who log normally after add a new guest.")
            else:
                raise FailException("Failed to check virt-who log normally after add a new guest.")
            # check if the uuid is correctly monitored by virt-who.
            self.vw_check_uuid(guestuuid, uuidexists=True)

        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # set interval to default
            cmd = "sed -i 's/.*VIRTWHO_INTERVAL=.*/#VIRTWHO_INTERVAL=5/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(logger, cmd, "restoring the interval time as default setting in virt-who config file")
            #.restart virtwho service
            self.vw_restart_virtwho_new()
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
