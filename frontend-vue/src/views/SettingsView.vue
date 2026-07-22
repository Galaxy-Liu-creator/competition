<template>
  <div class="page-wrap">
    <div class="page">
      <!-- 个人资料卡 -->
      <div class="card">
        <div class="profile">
          <div class="big-av">
            {{ user?.avatar_text || '安' }}
            <span class="cam" title="更换头像" @click="msg('头像上传即将开放')"><el-icon><Camera /></el-icon></span>
          </div>
          <div>
            <h3>{{ user?.name || '安全管理员' }}<span class="role">{{ user?.role || '系统管理员' }}</span></h3>
            <p>
              {{ user?.email || 'admin@qingan.com' }}
              <template v-if="user?.last_login_at"> · 上次登录 {{ user.last_login_at }}</template>
              <template v-if="user?.last_login_ip"> · IP {{ user.last_login_ip }}</template>
            </p>
          </div>
          <button type="button" class="edit" @click="openProfile">编辑资料</button>
        </div>
      </div>

      <!-- 外观偏好 -->
      <div class="card">
        <div class="hd">外观偏好</div>
        <div class="bd">
          <div class="pref">
            <div class="lab"><strong>主题模式</strong><span>选择日间、夜间或跟随系统</span></div>
            <div class="theme-cards">
              <div
                v-for="opt in themeOptions"
                :key="opt.value"
                class="tcard"
                :class="{ on: prefs.theme === opt.value }"
                @click="setTheme(opt.value)"
              >
                <div class="prev" :class="opt.value"></div>{{ opt.label }}
              </div>
            </div>
          </div>
          <div class="pref">
            <div class="lab"><strong>侧边栏默认收起</strong><span>进入系统时侧边栏保持折叠状态</span></div>
            <el-switch v-model="prefs.sidebarCollapsed" @change="save({ sidebarCollapsed: prefs.sidebarCollapsed })" />
          </div>
        </div>
      </div>

      <!-- 通知偏好 -->
      <div class="card">
        <div class="hd">通知偏好</div>
        <div class="bd">
          <div class="pref">
            <div class="lab"><strong>风险事件告警</strong><span>发生高危风险事件时站内推送提醒</span></div>
            <el-switch v-model="prefs.notifyRisk" @change="save({ notifyRisk: prefs.notifyRisk })" />
          </div>
          <div class="pref">
            <div class="lab"><strong>设备离线提醒</strong><span>吊车、摄像头等设备心跳异常时提醒</span></div>
            <el-switch v-model="prefs.notifyDeviceOffline" @change="save({ notifyDeviceOffline: prefs.notifyDeviceOffline })" />
          </div>
          <div class="pref">
            <div class="lab"><strong>审批待办提醒</strong><span>有新的审批待办时提醒</span></div>
            <el-switch v-model="prefs.notifyApproval" @change="save({ notifyApproval: prefs.notifyApproval })" />
          </div>
        </div>
      </div>

      <!-- 常规设置 -->
      <div class="card">
        <div class="hd">常规设置</div>
        <div class="bd">
          <div class="pref">
            <div class="lab"><strong>默认落地页</strong><span>登录后默认进入的页面</span></div>
            <el-select v-model="prefs.landingPage" style="width: 160px" @change="save({ landingPage: prefs.landingPage })">
              <el-option label="工作台" value="/workbench" />
              <el-option label="实时监控" value="/crane/monitor" />
              <el-option label="安全报表" value="/report" />
            </el-select>
          </div>
          <div class="pref">
            <div class="lab"><strong>登录密码</strong><span>建议定期更换密码以保障账号安全</span></div>
            <button type="button" class="btn-line" @click="passwordVisible = true">修改密码</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑资料弹窗 -->
    <el-dialog v-model="profileVisible" title="编辑资料" width="420px">
      <el-form label-width="72px">
        <el-form-item label="姓名"><el-input v-model="profileForm.name" maxlength="16" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="profileForm.email" /></el-form-item>
        <el-form-item label="头像字"><el-input v-model="profileForm.avatar_text" maxlength="1" style="width: 80px" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="profileVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="passwordVisible" title="修改密码" width="420px" @closed="resetPasswordForm">
      <el-form label-width="88px">
        <el-form-item label="原密码"><el-input v-model="passwordForm.old" type="password" show-password /></el-form-item>
        <el-form-item label="新密码"><el-input v-model="passwordForm.next" type="password" show-password placeholder="至少 6 位" /></el-form-item>
        <el-form-item label="确认新密码"><el-input v-model="passwordForm.confirm" type="password" show-password /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="savePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Camera } from '@element-plus/icons-vue'
import { auth, changePassword, loadMe, preferences, savePreferences, updateMe } from '@/auth'
import { applyTheme } from '@/theme'

const user = computed(() => auth.user)
const prefs = reactive({ ...preferences() })

const themeOptions = [
  { value: 'dark', label: '夜间模式' },
  { value: 'light', label: '日间模式' },
  { value: 'auto', label: '跟随系统' },
]

const profileVisible = ref(false)
const passwordVisible = ref(false)
const saving = ref(false)
const profileForm = reactive({ name: '', email: '', avatar_text: '' })
const passwordForm = reactive({ old: '', next: '', confirm: '' })

onMounted(async () => {
  await loadMe()
  Object.assign(prefs, preferences())
})

function msg(text) { ElMessage.info(text) }

async function save(patch) {
  try {
    await savePreferences(patch)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  }
}

function setTheme(mode) {
  prefs.theme = mode
  applyTheme(mode)
  save({ theme: mode })
}

function openProfile() {
  profileForm.name = user.value?.name || ''
  profileForm.email = user.value?.email || ''
  profileForm.avatar_text = user.value?.avatar_text || ''
  profileVisible.value = true
}

async function saveProfile() {
  saving.value = true
  try {
    await updateMe({ ...profileForm })
    profileVisible.value = false
    ElMessage.success('资料已更新')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

function resetPasswordForm() {
  passwordForm.old = passwordForm.next = passwordForm.confirm = ''
}

async function savePassword() {
  if (!passwordForm.old || passwordForm.next.length < 6) {
    ElMessage.warning('请填写原密码，新密码至少 6 位')
    return
  }
  if (passwordForm.next !== passwordForm.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  saving.value = true
  try {
    await changePassword(passwordForm.old, passwordForm.next)
    passwordVisible.value = false
    ElMessage.success('密码修改成功')
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data?.message || '密码修改失败')
    } else {
      passwordVisible.value = false
      ElMessage.success('密码修改成功(演示模式)')
    }
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.page-wrap { padding: 24px; }
.page { max-width: 900px; margin: 0 auto; display: grid; gap: 18px; }

.card { background: var(--qa-panel); border: 1px solid var(--qa-border); border-radius: var(--qa-radius-lg); }
.card .hd {
  padding: 16px 22px; border-bottom: 1px solid var(--qa-border);
  font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 8px;
}
.card .hd::before {
  content: ''; width: 3px; height: 15px; border-radius: 2px;
  background: linear-gradient(var(--qa-blue), var(--qa-cyan));
}
.card .bd { padding: 4px 22px; }

/* 个人资料卡 */
.profile { display: flex; align-items: center; gap: 20px; padding: 24px 22px; }
.big-av {
  position: relative; width: 72px; height: 72px; display: grid; place-items: center;
  background: linear-gradient(135deg, var(--qa-blue), #1d4ed8); color: #fff;
  font-size: 28px; border-radius: 50%;
  box-shadow: 0 6px 18px rgba(59, 130, 246, .35);
}
.big-av .cam {
  position: absolute; right: -2px; bottom: -2px; width: 26px; height: 26px;
  display: grid; place-items: center; font-size: 13px;
  background: var(--qa-panel-2); border: 1px solid var(--qa-border-strong);
  border-radius: 50%; cursor: pointer; color: var(--qa-text-2);
}
.profile h3 { margin: 0; font-size: 19px; }
.profile .role {
  display: inline-block; margin-left: 10px; font-size: 12px; color: var(--qa-cyan);
  background: var(--qa-cyan-dim); border: 1px solid rgba(34, 211, 238, .4);
  padding: 2px 10px; border-radius: 999px; vertical-align: 2px;
}
.profile p { margin: 6px 0 0; font-size: 13px; color: var(--qa-text-muted); }
.profile .edit {
  margin-left: auto; height: 36px; padding: 0 18px; font-family: inherit; font-size: 13.5px;
  color: var(--qa-blue); background: var(--qa-blue-dim);
  border: 1px solid rgba(59, 130, 246, .45); border-radius: 8px; cursor: pointer;
}
.profile .edit:hover { background: rgba(59, 130, 246, .22); }

/* 偏好行 */
.pref {
  display: flex; align-items: center; justify-content: space-between; gap: 16px;
  padding: 15px 0; border-bottom: 1px solid var(--qa-border);
}
.pref:last-child { border-bottom: 0; }
.pref .lab strong { display: block; font-size: 14px; font-weight: 500; }
.pref .lab span { display: block; margin-top: 3px; font-size: 12.5px; color: var(--qa-text-muted); }

/* 主题模式选择卡 */
.theme-cards { display: flex; gap: 12px; flex-wrap: wrap; }
.tcard {
  width: 108px; cursor: pointer; border: 1.5px solid var(--qa-border); border-radius: 10px;
  padding: 8px; text-align: center; font-size: 12.5px; color: var(--qa-text-2);
}
.tcard.on { border-color: var(--qa-blue); box-shadow: 0 0 0 3px rgba(59, 130, 246, .18); color: var(--qa-text); }
.tcard .prev { height: 52px; border-radius: 6px; margin-bottom: 7px; border: 1px solid var(--qa-border); }
.tcard .prev.dark { background: linear-gradient(135deg, #060d1a 55%, #0d1b30); }
.tcard .prev.light { background: linear-gradient(135deg, #f4f7fc 55%, #dde7f3); }
.tcard .prev.auto { background: linear-gradient(115deg, #f4f7fc 49.5%, #060d1a 50.5%); }

.btn-line {
  font-family: inherit; font-size: 13.5px; color: var(--qa-text);
  background: var(--qa-panel-2); border: 1px solid var(--qa-border); border-radius: 8px;
  height: 36px; padding: 0 12px; cursor: pointer;
}
.btn-line:hover { border-color: var(--qa-blue); color: var(--qa-blue); }
</style>
