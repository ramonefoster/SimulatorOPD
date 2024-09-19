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
    console.error('Error:', error);
  }
}


function preload() {
  base = loadModel("static/assets/Pilar_PE160.obj", false)
  eixo = loadModel("static/assets/Eixo_PE160.obj", false)
  tubo = loadModel("static/assets/Tubo_PE160.obj", false)
  inconsolata = loadFont('static/assets/inconsolata.otf')
  // data = loadJSON('static/assets/data.json')
  setInterval(getJSONData, 150)
}

function windowResized() {
  resizeCanvas(windowWidth, windowHeight);
}

function setup() {
  createCanvas(windowWidth, windowHeight, WEBGL)
  textFont(inconsolata)
  textSize(height / 45)
  textAlign(CENTER, CENTER)

  color_slider = createSlider(50, 150, 100);
  color_slider.position(10, 680)
  color_slider.style('width', multi_slider_size + 'px');

}
let value = -180;

function mouseDragged() {
  value = mouseX;

}

function draw() {
  background(color_slider.value())
  translate(-50, +50, 0)
  box(1);

  if (data) {  // Atualiza o valor apenas se ele realmente existir. Ação para que não apareça 'UNDEFINED' como resultado
    ah = data.hour_angle
    dec = data.declination
  }

  fill(150, 0, 100)
  // text('\nra_deg: ' + ra_deg() + '\ndec_deg: ' + dec_deg(), -260, 400)
  noFill()

  scale(.06)
  // normalMaterial()
  fill(45, 128, 217) // Atribui cor ao modelo
  stroke(1)

  rotateY(value * PI / 180)
  //translate(0, 0, 1785) //Offset para evidenciar a escrita

  // let DEC = dec_deg()
  // let RA_deg = ra_deg()

  rotateX(-202.25 * PI / 180) // É nessa linha que sera somado 22.5 graus
  model(base)
  //rotateZ(-millis() / 1000 * PI / 180 / 240) // Isso gira o RA ou sideral
  rotateZ(-ah*15 * PI / 180) // Aqui configura o valor do Eixo RA (+/-4,5 ah)

  translate(0, 0, 2397) //Offset para coincidir os pivôs da base e do eixo

  model(eixo)
  translate(-508, 0, 0) //Offset para coincidir os pivôs do eixo e do tubo
  rotateX(-22.25 * PI / 180)  // Aqui configura a Latitude
  rotateX(-1 * (dec) * PI / 180)  // Aqui configura o valor do eixo DEC (+57 N e -80 S)
  fill(246, 245, 240)
  model(tubo)
  


}

