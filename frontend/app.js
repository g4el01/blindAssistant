const API_BASE =
    window.location.origin;
	
const statusDiv =
document.getElementById(
    "status"
);

function hablar(texto){

    speechSynthesis.cancel();

    const msg =
    new SpeechSynthesisUtterance(
        texto
    );

    msg.lang="es-MX";

    speechSynthesis.speak(msg);
}

async function capturar(){

    const stream =
    await navigator
    .mediaDevices
    .getUserMedia({

        video:{
            facingMode:"environment"
        }

    });

    const video =
    document.createElement(
        "video"
    );

    video.srcObject =
    stream;

    await video.play();

    await new Promise(
        r=>setTimeout(r,700)
    );

    const canvas =
    document.createElement(
        "canvas"
    );

    canvas.width =
    video.videoWidth;

    canvas.height =
    video.videoHeight;

    canvas
    .getContext("2d")
    .drawImage(
        video,
        0,
        0
    );

    const image =
    canvas.toDataURL(
        "image/jpeg",
        0.8
    );

    stream
    .getTracks()
    .forEach(
        t=>t.stop()
    );

    return image;
}

async function enviar(
    endpoint
){

    try{

        statusDiv.innerText =
        "Capturando imagen...";

        const image =
        await capturar();

        statusDiv.innerText =
        "Analizando...";

        const response =
        await fetch(

            API_BASE + "/" + endpoint,

            {
                method:"POST",

                headers:{
                    "Content-Type":
                    "application/json"
                },

                body:JSON.stringify({
                    image:image
                })
            }
        );

        const data =
        await response.json();

        statusDiv.innerText =
        data.result;

        hablar(
            data.result
        );

    }

    catch(error){

        statusDiv.innerText =
        error.message;

        hablar(
            "Error"
        );
    }
}

document.addEventListener(

    "keydown",

    async function(e){

        const key =
        e.key.toLowerCase();

        if(key==="a"){

            hablar(
                "Modo ayuda para caminar"
            );

            await enviar(
                "environment"
            );
        }

        if(key==="b"){

            hablar(
                "Modo lectura"
            );

            await enviar(
                "ocr"
            );
        }

        if(key==="c"){

            hablar(
                "Modo contar dinero"
            );

            await enviar(
                "money"
            );
        }

		if(key==="d"){

            hablar(
                "Modo descripción de objeto"
            );

            await enviar(
                "object"
            );
        }
		
		if(key==="e"){

            hablar(
                "Modo clima"
            );

            await enviar(
                "weather"
            );
        }
    }
);
