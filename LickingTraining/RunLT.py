from LickingTraining.RunLickTraining import DAQtoLickTraining


LT = DAQtoLickTraining()
LT.cameras_on = True
LT.startAcquisition()
LT.start_training()
