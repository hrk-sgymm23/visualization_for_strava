# ====== 可変項目 ======
IMAGE ?= streamlit-app
TAG   ?= latest
PORT  ?= 8501
APP   ?= src/app.py
DOCKER?= docker

# ====== タスク ======
.PHONY: help build run dev stop logs shell clean prune

help:
	@echo "make build          # Dockerイメージをビルド"
	@echo "make run            # 本番モードで起動（コピーされたコード）"
	@echo "make dev            # 開発モードで起動（カレントをマウント、ホットリロード）"
	@echo "make logs           # コンテナのログをフォロー"
	@echo "make stop           # 実行中のコンテナを停止"
	@echo "make shell          # コンテナ内にシェルで入る（開発用）"
	@echo "make clean          # イメージ削除"
	@echo "make prune          # 未使用リソースの掃除"

build:
	$(DOCKER) build -t $(IMAGE):$(TAG) --build-arg APP=$(APP) .

run: stop
	$(DOCKER) run --rm -d \
		--name $(IMAGE) \
		-p $(PORT):8501 \
		$(IMAGE):$(TAG)

dev: stop
	# ローカルのソースをマウントしてホットリロード
	$(DOCKER) run --rm -d \
		--name $(IMAGE)-dev \
		-p $(PORT):8501 \
		-v $(PWD):/app \
		-w /app \
		$(IMAGE):$(TAG) \
		bash -lc "streamlit run $(APP) --server.port=8501 --server.address=0.0.0.0"

logs:
	-$(DOCKER) logs -f $(IMAGE)

stop:
	-$(DOCKER) stop $(IMAGE) >/dev/null 2>&1 || true
	-$(DOCKER) stop $(IMAGE)-dev >/dev/null 2>&1 || true

shell:
	$(DOCKER) run --rm -it \
		--name $(IMAGE)-shell \
		-v $(PWD):/app \
		-w /app \
		--entrypoint bash \
		$(IMAGE):$(TAG)

clean:
	-$(DOCKER) rmi $(IMAGE):$(TAG)

prune:
	$(DOCKER) system prune -f
