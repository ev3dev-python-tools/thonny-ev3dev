
mkdir -p context
cd context

git clone https://github.com/ev3dev-python-tools/ev3devcmd.git
git clone https://github.com/ev3dev-python-tools/ev3dev2simulator.git
git clone https://github.com/ev3dev-python-tools/ev3devrpyc.git
git clone https://github.com/ev3dev-python-tools/ev3devlogging.git

# we do not develop in thonny itself, but we clone it anyway in 
# the project so that we can easily launch with the python command:
#
#      python context/thonny/thonny/__main__.py
#
# we cannot commit to thonny; so we therefor clone only a single depth of
# specific branch to keep storage usage to a minimal
git clone -c advice.detachedHead=false --depth 1 --branch v3.2.6 https://github.com/thonny/thonny.git

cd ..
