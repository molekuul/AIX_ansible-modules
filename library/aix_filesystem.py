#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'supported_by': 'community',
    'status': ['preview']
}

DOCUMENTATION = '''
---
#version_added: "2.2"
author: "Bob ter Hark"
module: aix_filesystem
short_description: Create filesystem on AIX
description:
  - This module creates a file system on a AIX logical volume
version_added: "2.2"
options:
  mountpoint:
    description:
    - Target mount point
    aliases: mp
    required: true
  state:
    description:
    - Whether filesystem should be absent or present
    default: present
    required: false
  logicalvolume:
    description:
    - Target logical volume
    aliases: lv
    required: true
  fstype:
    description:
    - Filesystem type to be created, choices are jfs or jfs2
    aliases: type
    default: jfs2
  atrestart:
    choices: [ "yes", "no" ]
    default: "yes"
    description:
    - If yes, filesystem is mounted at system restart
    required: false
notes:
  - tested on AIX 7
  - uses crfs command
'''

EXAMPLES = '''
# Create a jfs2 type filesystem on logical volume lvol1 and mount it on
# /application at restart
- name: Create /application
  aix_filesystem:
    mp=/application
    lv=lvol1

# Create a jfs type filesystem /cluster on logical volume lvol2 and don't mount
# during system restart
- name: Create /cluster
  aix_filesystem:
    mp=/cluster
    fstype=jfs
    lv=lvol2
    atrestart=no

# Remove the filesystem /data from /etc/filesystems
# Note: filesystem should be unmounted
# Note2: Logical volume will be removed
- name: Remove /data
  aix_filesystem:
    mp=/data
    state=absent
'''

RETURN = ''' # '''

from ansible.module_utils.basic import *


def main():
    module = AnsibleModule(
        argument_spec=dict(
            mountpoint=dict(required=True, aliases=['mp']),
            state=dict(choices=['absent', 'present'], default='present'),
            logicalvolume=dict(aliases=['lv']),
            fstype=dict(choices=['jfs2', 'jfs'], default='jfs2',
                        aliases=['type']),
            atrestart=dict(type='bool', default='yes'),
        ),
        supports_check_mode=True,
    )

#    supported_fstypes = {'jfs', 'jfs2'}

    mp = module.params['mountpoint']
    state = module.params['state']
    lv = module.params['logicalvolume']
    fstype = module.params['fstype']
    atrestart = module.boolean(module.params['atrestart'])

    changed = False

    # check if filesystem exists
    # TODO if exists check fstype
    # TODO if exists check atrestart flag
    cmd = module.get_bin_path('lsfs', required=True)
    rc, out, err = module.run_command("%s %s" % (cmd, mp))
    if rc == 0:
        if state == 'present':
            module.exit_json(changed=False,
                             msg="Information: Filesystem (%s) already exists"
                             % (mp))
        else:
            # Filesystem is present and state is absent -> remove
            if module.check_mode:
                changed = True
                module.exit_json(changed=changed)
            else:
                # rmfs -r <mount-point>
                cmd = module.get_bin_path('rmfs', required=True)
                rc, out, err = module.run_command("%s -r %s" % (cmd, mp))
                if rc != 0:
                    module.fail_json(msg=("Error: Removing filesystem (%s)"
                                     "failed") % (mp), rc=rc, err=err)
                else:
                    changed = True
                    module.exit_json(changed=changed)
    else:
        if state == 'absent':
            # Filesystem is not present and state is absent -> success
            module.exit_json(changed=False,
                             msg="Information: Filesystem (%s) does not exists"
                             % (mp))
    # Filesystem is not present and state is present -> create
    # check if lv exists
    cmd = module.get_bin_path('lslv', required=True)
    rc, out, err = module.run_command("%s %s" % (cmd, lv))
    if rc != 0:
        module.fail_json(msg="Error: Logical volume %s does not exist." % (lv),
                         rc=rc, err=err)

    if module.check_mode:
        changed = True
    else:
        if atrestart:
            aflag = 'yes'
        else:
            aflag = 'no'

        # crfs  -v jfs2 -A yes -d <logical-volume> -m <mount-point>
        cmd = module.get_bin_path('crfs', required=True)
        if fstype == 'jfs2':
            rc, out, err = module.run_command(("%s -v %s -A %s -d %s -m %s"
                                              " -a logname=INLINE")
                                              % (cmd, fstype, aflag, lv, mp))
        else:
            rc, out, err = module.run_command("%s -v %s -A %s -d %s -m %s"
                                              % (cmd, fstype, aflag, lv, mp))

        if rc == 0:
            changed = True
        else:
            module.fail_json(msg=("Error: Creating filesystem %s on logical"
                             "volume %s failed.") % (mp, lv), rc=rc, err=err)

    module.exit_json(changed=changed)

if __name__ == '__main__':
    main()
