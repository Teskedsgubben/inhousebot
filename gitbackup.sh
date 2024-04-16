printf '%(%Y-%m-%d)T\n' -1 >> /home/felix/inhousebot/gitbackup.log
git stage games.json users.json >> /home/felix/inhousebot/gitbackup.log
git commit -m auto_data_backup >> /home/felix/inhousebot/gitbackup.log
git push >> /home/felix/inhousebot/gitbackup.log