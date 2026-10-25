import { chromium } from 'file:///C:/Users/10934/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs'
import fs from 'node:fs/promises'
import path from 'node:path'

const baseUrl = 'http://127.0.0.1:5178'
const outputDir = path.resolve('tmp/video/screens')
const fixtureDir = path.resolve('tmp/video/fixtures')
const edgePath = 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe'

await fs.mkdir(outputDir, { recursive: true })
await fs.mkdir(fixtureDir, { recursive: true })

const browser = await chromium.launch({
  executablePath: edgePath,
  headless: true,
  args: ['--font-render-hinting=none'],
})
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
  colorScheme: 'light',
  reducedMotion: 'reduce',
})
const page = await context.newPage()

async function open(route) {
  await page.goto(`${baseUrl}${route}`, { waitUntil: 'networkidle' })
  await page.evaluate(() => document.fonts.ready)
  await page.waitForTimeout(500)
}

async function shot(name) {
  await page.screenshot({ path: path.join(outputDir, `${name}.png`), fullPage: false })
}

await open('/')
await shot('01-dashboard')
await page.getByRole('button', { name: /350 ml/ }).first().click()
await page.waitForTimeout(300)
await shot('02-dashboard-water')

await open('/meal')
await shot('03-meal-upload')
const menuFixture = path.join(fixtureDir, 'menu-demo.png')
await page.locator('input[type="file"]').setInputFiles(menuFixture)
await page.waitForTimeout(300)
await shot('04-meal-image-ready')
await page.getByRole('button', { name: /开始智能识别/ }).click()
await page.waitForTimeout(1300)
await shot('05-meal-review')
await page.getByRole('button', { name: /确认并生成方案/ }).click()
await page.waitForTimeout(900)
await shot('06-meal-plans')
await page.locator('.plan-button').first().click()
await page.waitForTimeout(300)
await shot('07-meal-selected')

await open('/records')
await shot('08-records')
await page.getByRole('button', { name: '食品标签识别' }).click()
await page.waitForTimeout(300)
await shot('09-label-upload')
await page.locator('input[type="file"]').setInputFiles(menuFixture)
await page.getByRole('button', { name: /开始识别/ }).click()
await page.waitForTimeout(1300)
await shot('10-label-result')

await open('/insights')
await page.waitForTimeout(800)
await shot('11-insights-water')
await page.getByRole('button', { name: '活动', exact: true }).click()
await page.waitForTimeout(500)
await shot('12-insights-activity')

await open('/assistant')
await shot('13-assistant-intro')
await page.getByRole('button', { name: /白天应该怎样规律饮水/ }).click()
await page.waitForTimeout(1100)
await shot('14-assistant-citation')
await page.locator('textarea').fill('请诊断我的睡眠疾病')
await page.locator('form').evaluate((form) => form.requestSubmit())
await page.waitForTimeout(1100)
await shot('15-assistant-boundary')

await open('/settings')
await shot('16-settings')

await browser.close()
console.log(`Captured demo assets in ${outputDir}`)
