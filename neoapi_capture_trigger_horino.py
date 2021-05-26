#OpenCV,neoAPIをロード
import sys
import numpy
import cv2
import neoapi
import time
import logging

try:
    #log保存
    addlog = logging.getLogger()
    #コンソール用
    showlog = logging.StreamHandler()
    #ファイル保存用
    savelog = logging.FileHandler('test.log')
    logging.basicConfig(handlers=[savelog, showlog], level=logging.INFO, format='{asctime} [{threadName}] [{levelname}] {message}', style='{')
    
    print(":neoAPI example:")
    #ライブラリバージョン確認
    print(f"LibraryVersion:{neoapi.CamBase_GetLibraryVersion()}")
 
    #Cameraオブジェクト作成
    camera = neoapi.Cam()

    #カメラ初期化
    #Connect()の引数には"U3V"や"GEV"などインターフェイス指定や、"モデル名”などの型番指定以外に、
    #"IPアドレス"、"MACアドレス"、"シリアル番号"、"ユーザーID"、"USBPortID"、"U3VVisionGUID"などの固有情報指定も可能
    #インターフェイス指定や型番指定の場合、そのインターフェイスや型番ではじめに認識されたカメラが初期化される
    #引数省略してConnect()した場合は最初に認識しているカメラを制御開始
    camera.Connect()
    print(f"CameraModel:{camera.f.DeviceModelName.value} (Serial:{camera.f.DeviceSerialNumber.value})")
    
    #デバイスの設定変更はCameraオブジェクトのあとにf.～でFeature名を指定し、Set(～)で変更、Get()で現在値取得を行う
    #もしくはvalueプロパティ値を直接操作する
    #パラメータをリストから文字選択するIEnumeration型の場合はSetString(～)で変更、GetString()で現在値取得を行う
    #実行タイプの場合はExecute()を行う
    #Feature名はSDK付属ビュアーのCameraExplorerでメインメニューWidgets->CameraFeatureを選択することで設定ツリーから確認可能(Feature名に半角スペースは不要)
    #HasFeature()でそのFeatureをカメラが持っているかどうか確認
    #IsReadable()でそのFeatureの値を読み取れるかどうか確認
    #IsWritable()でそのFeatureの値が変更できるか確認

    #利用可能なFeature名一覧表示
    #print("CameraFeatures:%s"%dir(camera.f))

    #露光時間を取得
    print(f"ExposureTime = {camera.f.ExposureTime.GetString()} us")
    #読出時間を取得
    print(f"ReadoutTime = {camera.f.ReadOutTime.GetString()} us")
     
    #横画素数と縦画素数を取得
    cam_width = camera.f.Width.value
    cam_height = camera.f.Height.value
    print(f"Width = {cam_width} / Height = {cam_height}")

    #PixelFormatを取得
    camera.f.PixelFormat.SetString('BayerRG8')

    # camera.f.PixelFormat.SetString('BGR8')
    cam_pixelformat = camera.f.PixelFormat.GetString()
    print(f"PixelFormat = {cam_pixelformat}")
    if '10' in cam_pixelformat or '12' in cam_pixelformat:
        print("PixelFormat is not 8bit")
        sys.exit(0)

    #ホワイトバランス調整実行
    if camera.HasFeature('BalanceWhiteAuto') and camera.IsWritable('BalanceWhiteAuto'):
        camera.f.BalanceWhiteAuto.SetString('Once')
        print("White balance was adjusted!")

    #Chunkを設定
    #利用可能なChunk一覧、Feature名では[Chunk ~]と指定
    #print(camera.GetChunkNames())
    if camera.HasFeature('ChunkEnable') :
        camera.f.ChunkSelector.SetString('Image')
        camera.f.ChunkEnable.value = True
        camera.f.ChunkSelector.SetString('Timestamp')
        camera.f.ChunkEnable.value = True
        camera.f.ChunkModeActive.value = True
        print(f"Chunk: {camera.f.ChunkModeActive.value}")


    camera.f.ExposureTime.value = 1500000

    #TriggerModeを変更
    camera.f.TriggerMode.SetString('Off')


    addlog.info(f"PixelFormat = {cam_pixelformat}")
    addlog.info(f"TriggerMode = {camera.f.TriggerMode.GetString()} us")
    addlog.info(f"ExposureTime = {camera.f.ExposureTime.GetString()} us")
    addlog.info(f"ReadoutTime = {camera.f.ReadOutTime.GetString()} us")


    cv_key = 0
    cv2.namedWindow('Preview: Press ESC key for exit / Precc C Key SoftTrigger', cv2.WINDOW_AUTOSIZE)
    #ライブ表示
    #ESCキーを押すと停止
    while cv_key != 27 :     
        #Cキーを押すとソフトトリガ送信
        if cv_key == 99 :
            timecheck = time.perf_counter()
            #SoftwareTriggger発行
            camera.f.TriggerSoftware.Execute()
            
            #ユーザーバッファへ画像データを格納
            #タイムアウト値を設定しない場合のデフォルト値は400ms
            buffer = camera.GetImage(400)
            addlog.info(f"---ImageID[{buffer.GetImageID()}]---")
            addlog.info(f"Time Gap[Trigger() -> GetImage()]:{(time.perf_counter() - timecheck)*1000 }ms.")
                        
            #利用可能な関数一覧表示
            #print("Imagefunction:%s"%dir(buffer))
            
            #バッファが空かどうかチェック
            #取得がタイムアウトした場合は再度GetImage実行、取得できていれば取得したデータを処理
            if not buffer.IsEmpty() :
                timecheck = time.perf_counter()
                #取得したバッファ内のnumpy配列にアクセス
                if 'Bayer' in cam_pixelformat :
                    #BayerならConvertでカラーデータに変換して2DのNumpyArray取得
                    img = buffer.Convert('BGR8').GetNPArray().reshape(cam_height,cam_width,3)
                elif cam_pixelformat == 'RGB8' or cam_pixelformat == 'BGR8':
                    #RGBやBGRならそのまま2DのNumpyArray取得
                    img = buffer.GetNPArray().reshape(cam_height,cam_width,3)                
                else :
                    #Monoならそのまま2DのNumpyArray取得                
                    img = buffer.GetNPArray().reshape(cam_height,cam_width)                
                addlog.info(f"ProcessingTime[convert & reshape]:{(time.perf_counter() - timecheck)*1000 }ms.")
                
                #bmp保存(neoapi)
                timecheck = time.perf_counter()                
                buffer.Save(f'trigger{buffer.GetImageID()}.bmp')
                addlog.info(f"ProcessingTime[buffer.Save (bmp)]:{(time.perf_counter() - timecheck)*1000 }ms.")
                
                #png保存(opencv)
                timecheck = time.perf_counter()
                cv2.imwrite(f'trigger{buffer.GetImageID()}.png', img)
                addlog.info(f"ProcessingTime[cv2.imwrite (png)]:{(time.perf_counter() - timecheck)*1000 }ms.")
                
                #リサイズしてOpenCVのプレビュー画面へ表示
                #2DNumpyArrayはcv2.Matとして利用可能
                if cam_height > 1080 :
                    img_resize = cv2.resize(img, dsize=None, fx=0.33, fy=0.33)
                    cv2.imshow('Preview: Press ESC key for exit / Precc C Key SoftTrigger' , img_resize)
                else :
                    cv2.imshow('Preview: Press ESC key for exit / Precc C Key SoftTrigger' , img)
                
                #FrameIDと左上[0,0]の画素の輝度値表示
                if 'Bayer' in cam_pixelformat :
                    addlog.info(f"ImageTimestamp[{buffer.GetChunkList().__getitem__('Chunk Timestamp').value}ns]-BGR_data[X0,Y0]:{img[0][0]}")
                    addlog.info(f"---ImageID[{buffer.GetImageID()}]---")
                    print(f"ImageID[{buffer.GetImageID()}]-ImageTimestamp[{buffer.GetChunkList().__getitem__('Chunk Timestamp').value}ns]-BGR_data[X0,Y0]: {img[0][0]}\n\n")
                elif cam_pixelformat == "RGB8" :
                    addlog.info(f"ImageTimestamp[{buffer.GetChunkList().__getitem__('Chunk Timestamp').value}ns]-RGB_data[X0,Y0]:{img[0][0]}")
                    addlog.info(f"---ImageID[{buffer.GetImageID()}]---")
                    print(f"ImageID[{buffer.GetImageID()}]-ImageTimestamp[{buffer.GetChunkList().__getitem__('Chunk Timestamp').value}ns]-RGB_data[X0,Y0]: {img[0][0]}\n\n")
                elif cam_pixelformat == "BGR8" :
                    addlog.info(f"ImageTimestamp[{buffer.GetChunkList().__getitem__('Chunk Timestamp').value}ns]-BGR_data[X0,Y0]:{img[0][0]}")
                    addlog.info(f"---ImageID[{buffer.GetImageID()}]---")
                    print(f"ImageID[{buffer.GetImageID()}]-ImageTimestamp[{buffer.GetChunkList().__getitem__('Chunk Timestamp').value}ns]-BGR_data[X0,Y0]: {img[0][0]}\n\n")
                else :
                    addlog.info(f"ImageTimestamp[{buffer.GetChunkList().__getitem__('Chunk Timestamp').value}ns]-Mono_data[X0,Y0]:{img[0][0]}")
                    addlog.info(f"---ImageID[{buffer.GetImageID()}]---")
                    print(f"ImageID[{buffer.GetImageID()}]-ImageTimestamp[{buffer.GetChunkList().__getitem__('Chunk Timestamp').value}ns]-Mono_data[X0,Y0]: {img[0][0]}\n\n")                        
        #プレビュー画面の更新
        cv_key = cv2.waitKey(1)
        pass
    print("\n")   
    #OpenCVプレビュー画面破棄
    cv2.destroyAllWindows()

    if camera.HasFeature("ChunkEnable") :
        camera.f.ChunkModeActive.value = False
        print(f"Chunk: {camera.f.ChunkModeActive.value}")
    camera.f.TriggerMode.SetString("Off")
    print(f"TriggerMode = {camera.f.TriggerMode.GetString()}")
except :
    import traceback
    traceback.print_exc()
finally :
    print("example end")
    sys.exit(0)