import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 引入Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faFacebookF, faTwitter, faLinkedinIn } from '@fortawesome/free-brands-svg-icons'
import { faEye, faEyeSlash, faFile, faFileText, faImage, faMicrophone, faTrashCan } from '@fortawesome/free-solid-svg-icons'

// 添加图标到库中
library.add(faFacebookF, faTwitter, faLinkedinIn, faEye, faEyeSlash, faFile, faFileText, faImage, faMicrophone, faTrashCan)

// 引入Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 全局引入Element Plus图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册FontAwesomeIcon全局组件
app.component('FontAwesomeIcon', FontAwesomeIcon)

app.mount('#app')