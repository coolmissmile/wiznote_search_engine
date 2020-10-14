# cp *.sh *.py  ~/ssd/NETAC/kuaipan/code/python/wiz_note_search/
# for python 2.7.x
# not support python 3.x

set -e

if [ ! -f .depend.success ];then
    # check python
    which python || echo "Error: python not found!"
    which python || exit 255

    # check python version MUST be 2.7.x
    pythonIS27=`python --version  2>&1 | grep -oc "2.7" `
    if [ $pythonIS27 -eq 0 ];then
        echo "Error: python MUST be 2.7.x"
        exit 255
    fi

    # check pip
    which pip || echo "Error: pip not found!"
    which pip || exit 255

    # install other packages
    pip install markdown
    pip install bs4  # for BeautifulSoup
    pip install web.py 
    pip install jieba

    touch .depend.success
fi


