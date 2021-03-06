from utils import *
from testcases.virt_who.virtwhobase import VIRTWHOBase
from testcases.virt_who.virtwhoconstants import VIRTWHOConstants
from utils.exception.failexception import FailException

class tc_ID155120_ESX_check_guest_consumer_uuid_on_server(VIRTWHOBase):
    def test_run(self):
        case_name = self.__class__.__name__
        logger.info("========== Begin of Running Test Case %s ==========" % case_name)
        try:
            SAM_IP = get_exported_param("SERVER_IP")
            SAM_HOSTNAME = get_exported_param("SERVER_HOSTNAME")
            SAM_USER = VIRTWHOConstants().get_constant("SAM_USER")
            SAM_PASS = VIRTWHOConstants().get_constant("SAM_PASS")

            guest_name = VIRTWHOConstants().get_constant("ESX_GUEST_NAME")
            destination_ip = VIRTWHOConstants().get_constant("ESX_HOST")

            self.esx_start_guest(guest_name)
            guestip = self.esx_get_guest_ip(guest_name, destination_ip)
            guestuuid = self.esx_get_guest_uuid(guest_name, destination_ip)
            # register guest to SAM
            if not self.sub_isregistered(guestip):
                self.configure_host(SAM_HOSTNAME, SAM_IP, guestip)
                self.sub_register(SAM_USER, SAM_PASS, guestip)

            # get uuid of host and guest consumer
            cmd = "grep 'Sending update in hosts-to-guests mapping' /var/log/rhsm/rhsm.log | tail -1"
            ret, output = self.runcmd(cmd, "get host consumer uuid")
            hostuuid = output.split("{")[1].split(":")[0].strip()
            cmd = "subscription-manager identity | grep identity"
            ret, output = self.runcmd(cmd, "get guest subscription-manager identity", guestip)
            guestuuid = output.split(':')[1].strip()
            # check whether guest is included in host info
            cmd = "curl -u admin:admin -k https://%s/sam/api/consumers/%s" % (SAM_IP, hostuuid)
            ret, output = self.runcmd(cmd, "Check whether guest is included in host info")
            if ret == 0 and guestuuid in output:
                logger.info("Succeeded to check guest in host info.")
                self.assert_(True, case_name)
            else:
                raise FailException("Failed to check guest in host info.")
        except Exception, e:
            logger.error("Test Failed - ERROR Message:" + str(e))
            self.assert_(False, case_name)
        finally:
            if guestip != None and guestip != "":
                self.sub_unregister(guestip)
            self.esx_stop_guest(guest_name, destination_ip)
            logger.info("========== End of Running Test Case: %s ==========" % case_name)

if __name__ == "__main__":
    unittest.main()
