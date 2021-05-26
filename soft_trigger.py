#OpenCV,neoAPIをロード
import sys
import cv2
import neoapi
import numpy
import time
import logging
import datetime


try:
	
	res_logger = logging.getLogger('werkzeug')

	#================================================================
	#setup_logger
	#================================================================

	now = datetime.datetime.today().strftime("%Y-%m-%d--%H-%M-%S")

	logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
	handler = logging.FileHandler(f'test_process-{now}.log')
	handler.setFormatter(logFormatter)
	res_logger = logging.getLogger("result_logger")
	res_logger.setLevel(logging.INFO)
	res_logger.addHandler(handler)
		
	res_logger.info("start main")
    
	
	camera = neoapi.Cam()
	camera.Connect()
	#内部バッファ数の設定（設定しない場合のデフォルトは10枚）
	#バッファは最低でも2枚必要
	#camera.SetImageBufferCount()とcamera.SetImageBufferCycleCount()で設定したバッファ数の内容によってGetImage()で取得されるデータ順が異なる
	#[SetImageBufferCycleCount = 1]の場合はGetImage()した時点で最新のデータが渡される
	#[SetImageBufferCycleCount > 1]の場合はリングバッファへ格納されたデータの中で最も古いデータから順に渡される
	num_buffer = 10
	camera.SetImageBufferCount(num_buffer)
	camera.SetImageBufferCycleCount(num_buffer)
	print("ImageBufferCount:%d" %(camera.GetImageBufferCount()))


	res_logger.info(f"ImageBufferCount:{camera.GetImageBufferCount()}")

	#利用可能なFeature名一覧表示
	# print("CameraFeatures:%s"%dir(camera.f))

	#HasFeature()でそのFeatureをカメラが持っているかどうか確認
	#IsReadable()でそのFeatureの値を読み取れるかどうか確認
	#IsWritable()でそのFeatureの値が変更できるか確認
	#センサー温度の表示
	
	#露光時間を32000μsに変更
	camera.f.ExposureTime.value = 50000

	# camera.f.ExposureAuto.value = True
	# camera.f.ExposureAuto.SetString("On")
	
	print("Exposure = %dus" %(camera.f.ExposureAuto.value))
	print("Exposure = %dus" %(camera.f.ExposureTime.value))
	res_logger.info(f"Exposure ={camera.f.ExposureTime.value}")

	#フレームレートを30fpsに変更
	#camera.f.AcquisitionFrameRateEnable.value = False
	camera.f.AcquisitionFrameRateEnable.value = True
	print("FrameRateControll = %s" %camera.f.AcquisitionFrameRateEnable.value)
	if camera.f.AcquisitionFrameRateEnable.value == True :
		camera.f.AcquisitionFrameRate.value = 30
		print("FixedFrameRate = %dfps" %camera.f.AcquisitionFrameRate.value)

	 #Chunkを設定
    #利用可能なChunk一覧、Feature名では[Chunk ~]と指定
    #print(camera.GetChunkNames())
	if camera.HasFeature("ChunkEnable") :
		camera.f.ChunkSelector.SetString("Image")
		camera.f.ChunkEnable.value = True
		camera.f.ChunkSelector.SetString("Timestamp")
		camera.f.ChunkEnable.value = True
		camera.f.ChunkModeActive.value = True
		print("Chunk: %s" %camera.f.ChunkModeActive.value)


	#横画素数と縦画素数を取得
	cam_width = camera.f.Width.value
	cam_height = camera.f.Height.value
	print("Width = %d / Height = %d" %(cam_width, cam_height))

	res_logger.info(f"Width = {cam_width} / Height = {cam_height}")

	#PixelFormatを取得
	# camera.f.PixelFormat.SetString("RGB8")
	# camera.f.PixelFormat.SetString("BayerRG8")

	camera.f.PixelFormat.SetString("Mono8")
	cam_pixelformat = camera.f.PixelFormat.GetString()
	print("PixelFormat = %s"  %cam_pixelformat)

	res_logger.info(f"PixelFormat = {cam_pixelformat}")

	#TriggerModeを変更
	camera.f.TriggerMode.SetString("On")
	# camera.f.TriggerMode.SetString("Off")
	cam_triggermode = camera.f.TriggerMode.GetString()
	print("TriggerMode = %s"  %cam_triggermode)

	res_logger.info(f"TriggerMode = {cam_triggermode}")

	camera.f.TriggerSource.SetString("All")
	# camera.f.TriggerMode.SetString("Off")
	cam_triggermode = camera.f.TriggerSource.GetString()
	print("TriggerMode = %s"  %cam_triggermode)

	camera.f.TriggerActivation.SetString("RisingEdge")
	# # camera.f.TriggerMode.SetString("Off")
	cam_triggermode = camera.f.TriggerActivation.GetString()
	print("TriggerMode = %s"  %cam_triggermode)

	cam_triggermode = "On"

	#ホワイトバランス調整実行
	if camera.HasFeature("BalanceWhiteAuto") :
		camera.f.BalanceWhiteAuto.SetString("Once")
		print("White balance was adjusted!")

	data = []
	cv_key = 0
	cv2.namedWindow("Preview: Press ESC key for exit / Precc C Key SoftTrigger", cv2.WINDOW_AUTOSIZE)

	#ライブ表示
	#ESCキーを押すと停止
	while cv_key != 27 :
		#プレビューウィンドウの画面更新
		cv_key = cv2.waitKey(1)

		# #トリガーモード時
		# if 	cam_triggermode == "On" :
		# 	#Cキーを押すとソフトトリガ送信
		while cv_key == 99 :
			cv_key = cv2.waitKey(1)
			if cv_key == 27 :
				break
		#SoftwareTriggger発行
			camera.f.TriggerSoftware.Execute()

		# if 	cam_triggermode == "On" :
		# 	#Cキーを押すとソフトトリガ送信
			
		# 	if cv_key == 27 :
		# 		break
		# 	#SoftwareTriggger発行
		# 	# camera.f.TriggerSoftware.Execute()
	
		#設定しない場合のデフォルト値は400ms
		start = time.perf_counter()

		buffer = camera.GetImage()	
		if not buffer.IsEmpty() :	


			buffer.Save(f'trigger{buffer.GetImageID()}.bmp')	
			print(f"--------------------- buffer Save duration was {time.perf_counter() - start }s.")		

			res_logger.info(f"--------------------- buffer Save duration was {time.perf_counter() - start }s.")

			start1 = time.perf_counter()
		           
			# if buffer.GetImageID() == 2:
			# 	#バッファは他のリスト変数にappendして参照すると上書きされないようにロックされる
			# 	#ロックしたままだと利用できる内部バッファが減っていくので使い終わったらロックを解除する
			# 	#appendで隔離したバッファが(確保したバッファ数-1)を超える場合データ格納に利用できるバッファがなくなりGetImage()はエラーになる
			# 	data.append(buffer)
			# 	#BMPで保存
			# 	data[0].Save("test.bmp")
			# 	#popでリスト変数から削除する事で参照している内部バッファのロックは解除される
			# 	data.pop(0)
			#Bayerならカラーデータに変換
			if "Bayer" in cam_pixelformat :
				#各bitでカラー変換
				if "8" in cam_pixelformat :
					buffer_color = buffer.Convert("BGR8")
				elif "10" in cam_pixelformat :
					buffer_color = buffer.Convert("BGR10")
				elif "12" in cam_pixelformat :
					buffer_color = buffer.Convert("BGR12")
				#バッファ内のnumpy配列にアクセス
				img_1D_bayer = buffer.GetNPArray()
				img_1D = buffer_color.GetNPArray()
			else :
				#バッファ内のnumpy配列にアクセス
				img_1D = buffer.GetNPArray()
			
			#格納されている配列は1Dなのでreshapeで2Dに変換
			if cam_pixelformat == "BGR8" or cam_pixelformat == "RGB8" :
				img_2D = img_1D.reshape(cam_height,cam_width,3)
			elif "Bayer" in cam_pixelformat :
				img_2D_bayer = img_1D_bayer.reshape(cam_height,cam_width)
				img_2D = img_1D.reshape(cam_height,cam_width,3)
			else :
				img_2D = img_1D.reshape(cam_height,cam_width)

			#OpenCVでの表示用データ作成
			if "Bayer" in cam_pixelformat :
				#[0,0]の輝度値表示
				print("ImageID[{0}]-Bayer_data[X0,Y0]: {1}".format(buffer.GetImageID(), img_2D_bayer[0][0]))
				print("ImageID[{0}]-RGB_data[X0,Y0]: {1}".format(buffer.GetImageID(), img_2D[0][0]))

				res_logger.info(f"ImageID[{buffer.GetImageID()}]-Bayer_data[X0,Y0]: {img_2D_bayer[0][0]}")
				res_logger.info(f"ImageID[{buffer.GetImageID()}]-RGB_data[X0,Y0]: {img_2D[0][0]}")

				#8bit以外なら表示用8bitデータ作成
				if "8" in cam_pixelformat :
					img_display = img_2D
				elif "10" in cam_pixelformat :
					img_display = cv2.convertScaleAbs(img_2D, alpha = 0.25)	
				elif "12" in cam_pixelformat :
					img_display = cv2.convertScaleAbs(img_2D, alpha = 0.0625)	
			elif cam_pixelformat == "BGR8":
				#[0,0]の輝度値表示
				print("ImageID[{0}]-BGR_data[X0,Y0]: {1}".format(buffer.GetImageID(), img_2D[0][0]))

				res_logger.info(f"ImageID[{buffer.GetImageID()}]-BGR_data[X0,Y0]: {img_2D[0][0]}")

				img_display = img_2D
			elif cam_pixelformat == 'RGB8' :
				#[0,0]の輝度値表示
				print("ImageID[{0}]-RGB_data[X0,Y0]: {1}".format(buffer.GetImageID(), img_2D[0][0]))

				res_logger.info(f"ImageID[{buffer.GetImageID()}]-RGB_data[X0,Y0]: {img_2D[0][0]}")
				#表示用BGRデータ作成
				img_display = cv2.cvtColor(img_2D,cv2.COLOR_RGB2BGR)
			else :
				#[0,0]の輝度値表示
				print("ImageID[{0}]-Mono_data[X0,Y0]: {1}".format(buffer.GetImageID(), img_2D[0][0]))

				res_logger.info(f"ImageID[{buffer.GetImageID()}]-Mono_data[X0,Y0]: {img_2D[0][0]}")
				#8bit以外なら表示用8bitデータ作成
				if "8" in cam_pixelformat :
					img_display = img_2D
				elif "10" in cam_pixelformat :
					img_display = cv2.convertScaleAbs(img_2D, alpha = 0.25)	
				elif "12" in cam_pixelformat :
					img_display = cv2.convertScaleAbs(img_2D, alpha = 0.0625)

			cv2.imwrite(f'trigger{buffer.GetImageID()}.png', img_display)

			res_logger.info(f"= ==============Imgge Save duration was {time.perf_counter() - start }s. convert time is  {time.perf_counter() - start1 }s.")
			print(f"= ======  ========Imgge Save duration was {time.perf_counter() - start }s. convert time is  {time.perf_counter() - start1 }s.")

			#リサイズしてOpenCVのプレビューウィンドウへ表示
			# if cam_height > 1080 :
			# 	img_resize = cv2.resize(img_display, dsize=None, fx=0.33, fy=0.33)
			# 	cv2.imshow("Preview: Press ESC key for exit / Precc C Key SoftTrigger" , img_resize)
			# else :
			# 	cv2.imshow("Preview: Press ESC key for exit / Precc C Key SoftTrigger" , img_display)

		pass

	print("Example End")
	camera.f.TriggerMode.SetString("Off")

except (neoapi.Exception, Exception) as exc :
	print("error: ", exc.GetDescription())

sys.exit()


