<template>
    <div ref="glContainer" class="full-screen"></div>
</template>

<script setup>
    import { ref, onMounted, onBeforeUnmount } from 'vue';
    import * as THREE from 'three';
    import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
    import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

    const glContainer = ref(null);

    onMounted(() => {
        // 1. 建立 Scene / Camera / Renderer
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(
            60,
            glContainer.value.clientWidth / glContainer.value.clientHeight,
            0.1,
            1000
        );
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(
            glContainer.value.clientWidth,
            glContainer.value.clientHeight
        );
        glContainer.value.appendChild(renderer.domElement);

        // 2. OrbitControls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;

        // 3. 添加環境光
        scene.add(new THREE.AmbientLight(0xffffff, 1));

        // 4. 載入 GLB 模型
        const loader = new GLTFLoader();
        loader.load(
            'model.glb',  // 確保模型放在 public 下
            gltf => {
                const model = gltf.scene;
                model.rotation.x =  Math.PI/2;
                model.rotation.y =  Math.PI/2;
                scene.add(model);

                // 計算包圍盒並取得中心 / 尺寸
                const box = new THREE.Box3().setFromObject(model);
                const center = new THREE.Vector3();
                const size = new THREE.Vector3();
                box.getCenter(center);
                box.getSize(size);

                // 調整 camera.far 並更新投影矩陣
                const maxDim = Math.max(size.x, size.y, size.z);
                camera.far = maxDim * 10;
                camera.updateProjectionMatrix();

                // 拉遠係數 & 側邊偏移
                const distFactor = 3.0;  // 原本 1.2 → 2.5
                camera.position.set(
                    center.x,
                    center.y + size.y * distFactor,
                    center.z + center.z *0.5 // 微微側面
                );

                // 橫向俯視：把螢幕的「上方」設定成世界 Z 軸
                camera.up.set(0, 0, 1);

                // 對準模型中心
                camera.lookAt(center);
                controls.target.copy(center);

                // 限制極角（只能從俯視到水平）
                controls.minPolarAngle = 0;
                controls.maxPolarAngle = Math.PI / 2;
                controls.update();
            },
            xhr => console.log(`Loading ${(xhr.loaded / xhr.total * 100) | 0}%`),
            err => console.error(err)
        );

        // 5. 視窗尺寸變更時更新 camera & renderer
        function onResize() {
            camera.aspect = glContainer.value.clientWidth / glContainer.value.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(
                glContainer.value.clientWidth,
                glContainer.value.clientHeight
            );
        }
        window.addEventListener('resize', onResize);

        // 6. 動畫迴圈
        let req;
        function animate() {
            req = requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // 7. 清理
        onBeforeUnmount(() => {
            window.removeEventListener('resize', onResize);
            cancelAnimationFrame(req);
            renderer.dispose();
            controls.dispose();
        });
    });
</script>

<style>
    /* 讓容器真正填滿整個視窗 */
    .full-screen {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
</style>



