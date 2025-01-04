document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('textInput');
    const voiceSelect = document.getElementById('voiceSelect');
    const speedRange = document.getElementById('speedRange');
    const speedValue = document.getElementById('speedValue');
    const convertBtn = document.getElementById('convertBtn');
    const audioSection = document.querySelector('.audio-section');
    const audioPlayer = document.getElementById('audioPlayer');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorMessage = document.getElementById('errorMessage');

    speedRange.addEventListener('input', () => {
        speedValue.textContent = speedRange.value;
    });

    convertBtn.addEventListener('click', async () => {
        const text = textInput.value.trim();
        if (!text) {
            showError('请输入要转换的文本');
            return;
        }

        try {
            convertBtn.disabled = true;
            convertBtn.textContent = '转换中...';
            errorMessage.textContent = '';
            
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    voice: voiceSelect.value,
                    rate: speedRange.value
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '转换失败');
            }

            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            
            audioPlayer.src = audioUrl;
            audioSection.style.display = 'block';
            
            downloadBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = audioUrl;
                a.download = 'tts-audio.mp3';
                a.click();
            };

        } catch (error) {
            showError(error.message || '转换失败，请稍后重试');
            audioSection.style.display = 'none';
        } finally {
            convertBtn.disabled = false;
            convertBtn.textContent = '转换为语音';
        }
    });

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
}); 