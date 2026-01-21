from pyroute2 import IPRoute, NetlinkError

"""
Work in progress, network mask automation to connect with UR.
Current implementation is not working, does not activate the ethernet adapter with the set mask
"""
class NetworkManager:

    def __init__(self, interface_name: str):
        """
        Initialize with the target interface name. (Experimental)

        Arguments:
            interface_name (str): The name of the network interface to manage.
        """
        self.interface_name = interface_name

    def _get_interface_index(self, ip_route_instance):
        """
        Helper to resolve interface name to kernel index ID.

        Arguments:
            ip_route_instance (IPRoute): An active IPRoute instance.

        Returns:
            int: The kernel index of the interface.
        """
        idx_list = ip_route_instance.link_lookup(ifname=self.interface_name)

        if not idx_list:
            raise ValueError(f"Interface '{self.interface_name}' not found.")

        return idx_list[0]

    def set_subnet(self, ip_address: str, cidr_prefix: int):
        """
        Flushes old IPs, sets the new IP/Subnet, and brings the link up.

        Args:
            ip_address (str): The desired IP address to set.
            cidr_prefix (int): The CIDR prefix length for the subnet.
        """
        # Use IPRoute as a context manager to auto-close the socket
        with IPRoute() as ip:
            try:
                # 1. Resolve the Interface ID
                idx = self._get_interface_index(ip)
                print(f"[{self.interface_name}] Flushing existing addresses...")

                # 2. Flush old addresses to prevent conflicts
                ip.flush_addr(index=idx)
                print(f"[{self.interface_name}] Setting IP to {ip_address}/{cidr_prefix}...")

                # 3. Add the new address
                ip.addr('add', index=idx, address=ip_address, mask=cidr_prefix)

                # 4. Ensure the link is UP
                ip.link('set', index=idx, state='up')

                print(f"[{self.interface_name}] Configuration applied successfully.")

            except NetlinkError as e:
                print(f"Kernel Error (Netlink): {e}")
            except Exception as e:
                print(f"General Error: {e}")

    def down(self):
        """
        Helper to manually bring the interface down.
        """
        with IPRoute() as ip:
            try:
                idx = self._get_interface_index(ip)
                ip.link('set', index=idx, state='down')

                print(f"[{self.interface_name}] Interface is now DOWN.")
            except Exception as e:
                print(f"Error: {e}")