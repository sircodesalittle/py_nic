import netifaces as ni
import winreg as wr
from subprocess import Popen
from pprint import pprint   


class NIC(object):
    """Representation for a network interface controller.
    
    General Usage:
        >>> from py_nic import NIC
        >>> import netifaces
        >>> interfaces = netifaces.interfaces()
        >>> interfaces
        ['{13F0A378-2ED4-4DC1-BFC1-B60992774E9C}', 
         '{544809C3-2F7E-42FE-81FC-737E18CE6CEE}']
        >>> nic_1 = NIC(intefaces[0])
        >>> nic_1
        Local Area Connection
        >>> nic_1.ipv4
        [{'netmask': '255.255.255.255', 
          'addr': '192.168.168.168', 
          'broadcast': '192.168.168.168'}]
        
    Adding an address:
        >>> nic_1.add_address('192.168.168.15')
        Success - 192.168.168.15 added to interface Local Area Connection
        >>> nic_1.ipv4
        [{'netmask': '255.255.255.255', 
          'addr': '192.168.168.168', 
          'broadcast': '192.168.168.168'}, 
         {'netmask': '255.255.255.0', 
          'addr': '192.168.168.15', 
          'broadcast': '192.168.168.255'}]
          
    Removing an address:
        >>> nic_1.delete_address('192.168.168.15')
        Success - 192.168.168.15 removed from Local Area Connection 
        >> nic_1.ipv4
        [{'netmask': '255.255.255.255', 
          'addr': '192.168.168.168', 
          'broadcast': '192.168.168.168'}]
        
    Remove all addresses:
        >>> nic_1.ipv4
        [{'netmask': '255.255.255.255', 
          'addr': '192.168.168.168', 
          'broadcast': '192.168.168.168'}, 
         {'netmask': '255.255.255.0', 
          'addr': '192.168.168.15', 
          'broadcast': '192.168.168.255'}]
        >>> nic_1.delete_all_addresses('192.168.168.10')
        Success - 192.168.168.15 added to interface Local Area Connection
        Success - 192.168.168.15 removed from Local Area Connection
        Success - 192.168.168.168 removed from Local Area Connection
        >>> nic_1.ipv4
        [{'netmask': '255.255.255.255', 
          'addr': '192.168.168.10', 
          'broadcast': '192.168.168.10'}]
    """
    
    def __init__(self, interface):
        """
        Args:
            interface (str): The windows ugly name of an interface (e.g. "{13F0A378-2ED4-4DC1-BFC1-B60992774E9C}" 
                translates to "Local Area Network") this value normally comes from the netifaces.interfaces() method.
        """
        self.interface = interface
        self.name = get_connection_name_from_guid(interface)
        self.ipv4 = get_ipv4(interface)
        
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()
        
    def add_address(self, ip_address, mask='255.255.255.0'):
        """Adds an address to the interface.
        
        Note:
            Must be run as administrator.
            
        Args:
            ip_address (str): The IPv4 address to be added to the interface.
            mask Optional[str]: The IPv4 mask for the address being added to the NIC
        """
        str_command = 'netsh interface ipv4 add address "{}" {} {}'.format(self.name, ip_address, mask)
        command = Popen(str_command)   
        stdout, stderr = command.communicate()
        if stdout is None and stderr is None:
            print('Success - {} added to interface {}'.format(ip_address, self.name))
        else:
            print('Failure - {} added to interface {}'.format(ip_address, self.name))
            print('\t' + str(stdout))
            print('\t' + str(stderr))
        self = self.__init__(self.interface)
        
    def delete_address(self, ip_address):
        """Deletes an address from the interface.
        
        Note:
            Must be run as administrator.
        
        Args:
            ip_address (str): The IPv4 address to be added to the interface.
        """
        str_command = 'netsh interface ipv4 delete address "{}" addr={}'.format(self.name, ip_address)
        command = Popen(str_command)   
        stdout, stderr = command.communicate()
        if stdout is None and stderr is None:
            print('Success - {} removed from {}'.format(ip_address, self.name))
        else:
            print('Failure - {} was not removed from {}'.format(ip_address, self.name))
            print('\t' + str(stdout))
            print('\t' + str(stderr))
        self = self.__init__(self.interface)
        
    def delete_all_addresses(self, default_address, mask='255.255.255.0'):
        """Deletes all the addresses for the interface, and adds (or leaves) the default address.
        
        Note:
            Must be run as administrator.
            
        Args:
            default_address (str): The IP address to leave on an interface.
        """
        self.add_address(default_address, mask)
        for address in self.ipv4:
            if address['addr'] != default_address:
                self.delete_address(address['addr'])
            

def get_connection_name_from_guid(iface_guid):
    """Converts the name provided by netifaces for an interface to be its readable Windows name.
    
    Args:
        iface_guid (str): The Windows name for an interface.
        
    Returns:
        str: The pretty Windows representation for the name of an interface.
        
    Examples:
        >>> interfaces = netifaces.interfaces()
        >>> print(interfaces[0])
        {13F0A378-2ED4-4DC1-BFC1-B60992774E9C}
        >>> pretty_name = get_connection_name_from_guid(interfaces[0])
        >>> print(pretty_name)
        Local Area Connection
        
        
    """
    iface_name = '(unknown)'
    reg = wr.ConnectRegistry(None, wr.HKEY_LOCAL_MACHINE)
    reg_key = wr.OpenKey(reg, r'SYSTEM\CurrentControlSet\Control\Network\{4d36e972-e325-11ce-bfc1-08002be10318}')
    try:
        reg_subkey = wr.OpenKey(reg_key, iface_guid + r'\Connection')
        iface_name = wr.QueryValueEx(reg_subkey, 'Name')[0]
    except FileNotFoundError:
        pass
    return iface_name


def get_ipv4(interface):
    """Gets the IPv4 connection parameters as a list of dictionaries
    
    Args:
        interface (str): netifaces.interfaces() like name (e.g. "{13F0A378-2ED4-4DC1-BFC1-B60992774E9C}")
        
    Returns:
        [dict]: List of dictinaries containing IPv4 connection info for the interface.
            Each dictionary contains the following keys: "addr", "netmask", "broadcast".
            
    Examples:
        >>> interfaces = netifaces.interfaces()
        >>> print(interfaces[0])
        {13F0A378-2ED4-4DC1-BFC1-B60992774E9C}
        >>> print(get_ipv4(interfaces[0]))
        [{'addr': '192.168.168.168', 
          'netmask': '255.255.255.255', 
          'broadcast': '192.168.168.168'}]
    """
    try:
        ipv4 =  ni.ifaddresses(interface)[ni.AF_INET]
        return ipv4
    except KeyError:
        return None

