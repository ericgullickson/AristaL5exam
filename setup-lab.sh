#!/bin/bash
#
#Makes sure galaxy is up to date
ansible-galaxy collection install arista.eos
ansible-galaxy collection install arista.cvp
ansible-galaxy collection list | grep arista