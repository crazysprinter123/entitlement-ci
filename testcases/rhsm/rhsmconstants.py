from utils import *
from utils.tools.shell.command import Command
from testcases.rhsm.rhsmguibase import RHSMGuiBase
from utils.exception.failexception import FailException

class RHSMConstants(RHSMGuiBase):
    sam_cons6 = {
            "username": "admin",
            "password": "admin",
            "baseurl": "https://samserv.redhat.com:443",
            "prefix": "/sam/api",
            "autosubprod": "Red Hat Enterprise Linux Server",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "SYS0395",
            "pid": "69",
            "pkgtoinstall": "zsh",
            "productrepo": "rhel-6-server-rpms",
            "betarepo": "rhel-6-server-beta-rpms",
            "servicelevel": "Premium",
            "releaselist": "6.1,6.2,6.3,6.4,6.5,6.6,6Server",
            }
    sam_cons7 = {
            "username": "admin",
            "password": "admin",
            "baseurl": "https://samserv.redhat.com:443",
            "prefix": "/sam/api",
            "autosubprod": "Red Hat Enterprise Linux Server",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "SYS0395",
            "pid": "69",
            "pkgtoinstall": "zsh",
            "productrepo": "rhel-7-server-rpms",
            "betarepo": "rhel-7-server-beta-rpms",
            "servicelevel": "Premium",
            "releaselist": "7.0,7Server",
            }
    stage_cons = {
            "username": "stage_test_12",
            "password": "redhat",
            "baseurl": "https://subscription.rhn.stage.redhat.com:443",
            "prefix": "/subscription",
            "autosubprod": "Red Hat Enterprise Linux Server",
            "installedproductname": "Red Hat Enterprise Linux Server",
            "productid": "RH0103708",
            "pid": "69",
            "pkgtoinstall": "zsh",
            "productrepo": "rhel-6-server-rpms",
            "betarepo": "rhel-6-server-beta-rpms",
            "servicelevel": "PREMIUM",
            "releaselist": "6.1,6.2,6.3,6.4,6Server",
            }
    candlepin_cons = {
            "username": "qa@redhat.com",
            "password": "HWj8TE28Qi0eP2c",
            # please install a localcandlepin whose hostname is localcandlepin.redhat.com
            "baseurl": "https://localcandlepin.redhat.com:8443",
            }

    server = ""
    paramdict = {}
    confs = None
    __instance = None
    samhostip = None
    samhostname = None
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RHSMConstants, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if(self.__initialized): return
        self.__initialized = True

        self.server = get_exported_param("RUN_SERVER")
        if self.server == "sam":
            # Run by delivered param
            self.samhostip = get_exported_param("SAM_IP")
            self.samhostname = get_exported_param("SAM_HOSTNAME")
            self.configure_sam_host(self.samhostname, self.samhostip)
        elif self.server == "stage":
            stage_name = self.get_delivered_param("STAGE_NAME")
            self.configure_stage_host(stage_name)
        elif self.server == "candlepin":
            pass

    def configure_sam_host(self, samhostname, samhostip):
        ''' configure the host machine for sam '''
        if samhostname != None and samhostip != None:
            # add sam hostip and hostname in /etc/hosts
            cmd = "sed -i '/%s/d' /etc/hosts; echo '%s %s' >> /etc/hosts" % (samhostname, samhostip, samhostname)
            ret, output = Command().run(cmd)
            if ret == 0:
                logger.info("Succeeded to configure /etc/hosts")
            else:
                raise FailException("Failed to configure /etc/hosts")
            # config hostname, prefix, port,   and repo_ca_crt by installing candlepin-cert
            cmd = "rpm -qa | grep candlepin-cert-consumer"
            ret, output = Command().run(cmd)
            if ret == 0:
                logger.info("candlepin-cert-consumer-%s-1.0-1.noarch has already exist, remove it first." % samhostname)
                cmd = "rpm -e candlepin-cert-consumer-%s-1.0-1.noarch" % samhostname
                ret, output = Command().run(cmd)
                if ret == 0:
                    logger.info("Succeeded to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
                else:
                    raise FailException("Failed to uninstall candlepin-cert-consumer-%s-1.0-1.noarch." % samhostname)
            cmd = "rpm -ivh http://%s/pub/candlepin-cert-consumer-%s-1.0-1.noarch.rpm" % (samhostip, samhostname)
            ret, output = Command().run(cmd)
            if ret == 0:
                logger.info("Succeeded to install candlepin cert and configure the system with sam configuration as %s." % samhostip)
            else:
                raise FailException("Failed to install candlepin cert and configure the system with sam configuration as %s." % samhostip)

    def configure_stage_host(self, stage_name):
        ''' configure the host machine for stage '''
        # configure /etc/rhsm/rhsm.conf to stage candlepin
        cmd = "sed -i -e 's/hostname = subscription.rhn.redhat.com/hostname = %s/g' /etc/rhsm/rhsm.conf" % stage_name
        ret, output = Command().run(cmd)
        if ret == 0:
            logger.info("Succeeded to configure rhsm.conf for stage")
        else:
            raise FailException("Failed to configure rhsm.conf for stage")

    def get_constant(self, name, targetmachine_ip=None):
#         if self.server == "sam":
#             if name == "baseurl" and self.get_delivered_param("SAM_HOSTNAME") != "":
#                 return "https://%s:443" % self.get_delivered_param("SAM_HOSTNAME")
#             else:
#                 print self.get_os_serials(targetmachine_ip)
        if self.get_os_serials(targetmachine_ip) == "6":
            return self.sam_cons6[name]
        elif self.get_os_serials(targetmachine_ip) == "7":
            return self.sam_cons7[name]
#         elif self.server == "stage":
#             return self.stage_cons[name]
#         elif self.server == "candlepin":
#             return self.candlepin_cons[name]

    def get_os_serials(self, targetmachine_ip=None):
        cmd = "uname -r | awk -F \"el\" '{print substr($2,1,1)}'"
#         (ret, output) = Command().run(cmd, comments=False)
        (ret, output) = self.runcmd(cmd, "", targetmachine_ip)
        if ret == 0:
            return output.strip("\n").strip(" ")
            logger.info("It's successful to get system serials.")
        else:
            logger.info("It's failed to get system serials.")
