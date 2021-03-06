from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID322862_kvm_unregister_check_output(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")
            rhsmlogpath='/var/log/rhsm/rhsm.log'
            # Modify the virt-who refresh interval
            cmd = "sed -i 's/#VIRTWHO_INTERVAL=.*/VIRTWHO_INTERVAL=100/' /etc/sysconfig/virt-who"
            (ret, output) = self.runcmd(logger, cmd, "changing interval to 100s in virt-who config file")
            if ret == 0:
                logger.info("Succeeded to set VIRTWHO_INTERVAL=100.")
            else:
                raise FailException("Failed to set VIRTWHO_INTERVAL=100.")
            # restart virtwho service
            self.service_command("restart_virtwho")
            # unregister hosts
            self.sub_unregister()
            # check virt-who log
            cmd = "tail -200 %s " % rhsmlogpath
            ret, output = self.runcmd(logger, cmd, "check output in rhsm.log")
            if ret == 0:
                if ("raise Disconnected" not in output) and ("Error while checking server version" not in output) and ("Connection refused" not in output):
                    logger.info("Success to check virt-who log normally after unregister system.")
                else:
                    raise FailException("Failed to check virt-who log normally after unregister system.")
            self.assert_(True, case_name)
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            # register host
            self.sub_register(SAM_USER, SAM_PASS)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
