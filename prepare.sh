# cp *.sh *.py  ~/ssd/NETAC/kuaipan/code/python/wiz_note_search/
# for python 2.7.x
# not support python 3.x


if [ ! -f .depend.success ];then
    # check python
    which python || echo "Error: python not found!"
    which python || exit 255

    # check python version MUST be 3.10

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


