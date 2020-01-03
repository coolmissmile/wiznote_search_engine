
WEBPORT=9009
curl -s http://127.0.0.1:${WEBPORT}/update_notelist
# .wiz_note_set.raw

find ~/.wiznote/*/data/notes  -type f | grep -o "{.*" > .wiz_note_set.ori.raw

# 寻找被删除的笔记
sort .wiz_note_set.raw .wiz_note_set.ori.raw .wiz_note_set.ori.raw | uniq -u | while read line;
do
    curl -s -X DELETE http://127.0.0.1:${WEBPORT}/delete_index/${line}
done

