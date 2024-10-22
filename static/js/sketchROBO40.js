let base
let eixo
let tubo

let inconsolata
let data = {}
let date, hour, ah, dec, cup, tube
let color_slider
let multi_slider_size = 150


async function getJSONData() {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/telescope/position');
    
    data = await response.json();
    
  } catch (error) {
    console.error('Error JSON data:', error);
  }
}

function preload() {
  eixo = loadModel("static/assets/robo40/_eixoPolar_simplified.obj", false)
  tubo = loadModel("static/assets/robo40/_tubo_conj_simplified.obj", false)
  base = loadModel("static/assets/robo40/_pilar_simplified.obj", false)
  inconsolata = loadFont('static/assets/Inconsolata.otf')
  setInterval(getJSONData, 500)
}


function setup() {
  createCanvas(windowWidth, windowHeight, WEBGL)
  textFont(inconsolata)
  textSize(height / 45)
  textAlign(CENTER, CENTER)

  color_slider = createSlider(50, 150, 100);
  color_slider.position(10, 820)
  color_slider.style('width', multi_slider_size + 'px');

}
let value = -180;

function mouseDragged() {
  value = mouseX;

}

function draw() {
  background(color_slider.value())

  if (data) {  // Atualiza o valor apenas se ele realmente existir. Ação para que não apareça 'UNDEFINED' como resultado
    ah = data.hour_angle
    dec = data.declination
    if (ah > 0) {
      ah = ah - 12
      dec = 180 - dec
    } 
  } else {
    ah = 0
    dec = -22.5
  }

  // fill(150, 0, 100)
  noFill()

  scale(.28)
  // normalMaterial()
  fill(152, 13, 59) // Atribui cor ao modelo  

  rotateY(value * PI / 180)

  rotateX(-202.25 * PI / 180) // É nessa linha que sera somado 22.5 graus
  strokeWeight(.1)
  model(base)
  rotateZ(-ah*15 * PI / 180) // Aqui configura o valor do Eixo RA (+/-4,5 ah)

  translate(0, 0, 0) //Offset para coincidir os pivôs da base e do eixo

  strokeWeight(.1)
  model(eixo)
  translate(260, 0, 0) //Offset para coincidir os pivôs do eixo e do tubo
  rotateX(-22.25 * PI / 180)  // Aqui configura a Latitude
  rotateX(-1 * (dec) * PI / 180)  // Aqui configura o valor do eixo DEC (+57 N e -80 S)
  fill(246, 245, 240)
  strokeWeight(.5)
  model(tubo)

}

