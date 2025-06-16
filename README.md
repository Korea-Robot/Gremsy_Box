# Gremsy_Box

![](assets/Gremsy_Box.png)

**Gremsy API + MediaMTX Proxy + Web Stream & Control**

---


## 📦 MediaMTX Docker 실행

### 기본 실행

```bash
docker run --rm -it --network=host bluenviron/mediamtx:latest
````

> ⚠️ RTSP 스트리밍을 위해 `--network=host` 플래그가 필요합니다.
> Docker가 UDP 패킷의 소스 포트를 변경할 수 있어, 서버가 클라이언트를 식별하지 못할 수 있습니다.

---

### `--network=host` 옵션을 사용할 수 없는 경우

RTSP UDP 전송 프로토콜을 비활성화하고 서버 IP를 추가하고 MTX_WEBRTCADDITIONALHOSTS포트를 수동으로 노출할 수 있습니다.

(Windows, Kubernetes 등)

```bash
docker run --rm -it \
  -e MTX_RTSPTRANSPORTS=tcp \
  -e MTX_WEBRTCADDITIONALHOSTS=192.168.x.x \
  -p 554:8554 \
  -p 1935:1935 \
  -p 8888:8888 \
  -p 8889:8889 \
  -p 8890:8890/udp \ #이미 로봇에서 쓰는중.
  -p 8189:8189/udp \
  bluenviron/mediamtx
```

---

## ▶️ Proxy 설정

`start_mediamtx.sh` 스크립트를 통해 MediaMTX를 실행하고, RTSP 스트림을 프록시합니다:

```bash
./start_mediamtx.sh
```

---

## ⚙️ 설정 파일 (`mediamtx.yml`)

```yaml
paths:
  gremsy:
    source: rtsp://192.168.168.240:554/payload #설정해 놓은 gremsy ip
```

* 위 설정을 적용하면:

  ```
  rtsp://<robot-ip>:554/gremsy
  ```

  로 스트림에 접근할 수 있습니다.

---

## 🔍 스트림 확인 (curl)

1. **RTSP DESCRIBE 요청**
   RTSP 핸드셰이크 확인용:

   ```bash
   curl -v rtsp://<robot-ip>:8554/gremsy
   ```

2. **MediaMTX HTTP API**
   등록된 경로 확인:

   ```bash
   curl http://<robot-ip>:8888/api/paths
   ```


이제. 로봇에 연결되어있는 카메라 아이피는 mediamtx를 통해 외부에서 볼수있는상태가 되었고, 이제 curl 명령어를 외부에서 컨트롤할수있게 해야하는데 어떻게 할수있을지 알려줘.

제일 좋은 방법은 로봇에서 서버를 실행시키고 그 로봇아이피에 연결하면 웹페이지가 뜨면서 카메라 스트림도 보이고 
짐벌제어를 할수있는 페이지도 보이는거야.