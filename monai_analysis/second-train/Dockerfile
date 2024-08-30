FROM projectmonai/monai:1.3.0

ADD cp_work_dir /home/ec2-user/choroid_plexus/cp_work_dir22

ADD ensemble_predict.py /bin/ensemble_predict.py
RUN chmod 755 /bin/ensemble_predict.py

RUN mkdir /work
