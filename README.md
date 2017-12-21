Role Name
=========
modules-role
This role holds all custom modules

Installation
------------
Add the following lines to the requirements.yml in your roles subdirectory:
<pre>
---
- src: ssh://git@gitlab.ing.net:2222/ISS-PaaS/modules-role.git
  scm: git
...
</pre>

Install from your projects top directory with:
<code>ansible-galaxy install -r roles/requirements.yml -p roles --force</code>

And finally add next lines in your playbook before starting any tasks:
<pre>
---
  roles:
  - modules-role
...
</pre>

Content
-------
<pre>
|-- library
|   |-- aix_facts.py
|   |-- aix_inittab.py
|   |-- aix_ipsec.py
|   |-- aix_nimclient
|   |-- aix_filesystem.py
|   |-- aix_efix.py
|   |-- aix_mount.py
|   |-- aix_lvol.py
|   |-- aix_update_all.py
|-- meta
|   |-- main.yml
|-- README.md
</pre>

In the library directory we have three custom modules included (and more will follow, because by default Ansible modules are not always compatible or suitable for AIX):
- aix_facts.py
This module will collect more facts than default and is run every time the main-role is processed from a playbook
- aix_inittab.py
A custom module to add/remove/update initab entries on AIX
- aix_ipsec.py
A module to enforce a IPsec rules
- aix_nimclient
A module to install and remove filesets, and to update the nimclient to latest level. No checking is build in. More documentation in Confluence
- aix_filesystem.py
A module to create (present) or remove (absent) filesystems
- aix_mount.py
A module to mount (present) or umount (absent) filesystems
Either a filesystem from /etc/filesystems or a NFS mount
- aix_efix.py
A module to install (present) or remove(absent) efixes

aix_filesystem
--------------
Example playbook
<pre>
- name: logical volumes present
  aix_lvol:
    vg: midwarevg
    lv: datalv
    size: 1024M

- name: file systems created
  aix_filesystem:
    mp: "/datafs"
    lv: "datalv"

- name: file systems mounted
  aix_mount:
    filesystem: /datafs
</pre>

aix_lvol
--------
<pre>
- name: Create a logical volume of 512M.
  aix_lvol:
    vg: testvg
    lv: testlv
    size: 512M

- name: Create a logical volume of 512M with disks hdisk1 and hdisk2
  aix_lvol:
    vg: testvg
    lv: test2lv
    size: 512M
    pvs: hdisk1,hdisk2

- name: Extend the logical volume to 1200M.
  aix_lvol:
    vg: testvg
    lv: test4lv
    size: 1200M


- name: Remove the logical volume.
  aix_lvol:
    vg: testvg
    lv: testlv
    state: absent
</pre>

aix_ipsec
---------
Playbook examples
<pre>
# Add a rule before the deny rule for interface en0
- name: Add permit rule for en0 from ip 4.3.2.1/32 port 1234 to any port at ip 1.2.3.4/32
  aix_ipsec:
    state: present
    action: 'permit'
    destination_address: '1.2.3.4'
    destination_mask: '255.255.255.255'
    destination_port_operation: 'any'
    destination_port: '0'
    source_address: '4.3.2.1'
    source_mask: '255.255.255.255'
    source_port_operation : 'eq'
    source_port: '1234'
    intf: 'en0'

# Add a rule from ip 4.3.2.1/32 that equals port 1234 to ip 1.2.3.4/24 equals port 1234 at the end of the rules.
- name: Add permit rule for port 1234
  aix_ipsec:
    state: present
    action: 'permit'
    destination_address: '1.2.3.4'
    destination_mask: '255.255.255.0'
    destination_port_operation: 'eq'
    destination_port: '1234'
    source_address: '4.3.2.1'
    source_mask: '255.255.255.255'
    source_port_operation : 'eq'
    source_port: '1234'

# remove a rule
- name: Remove Rule
  aix_ipsec:
    state: absent
    action: 'permit'
    destination_address: '1.2.3.4'
    destination_mask: '255.255.255.255'
    destination_port_operation: 'any'
    destination_port: '0'
    source_address: '4.3.2.1'
    source_mask: '255.255.255.255'
    source_port_operation : 'eq'
    source_port: '1234'
    intf: 'en0'
</pre>

aix_updata_all
--------
<pre>
  - name: update_all from lpp_new
    aix_update_all:
    become: true
    tags: update_all

  - name: update_all from uuc_repos
    aix_update_all:
      nfs_share: /uuc_repos/2013_1
    become: true
    tags: update_all
</pre>


Author Information
------------------
ING / Infra / AIX squad
