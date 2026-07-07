const { createApp, nextTick } = Vue;

const app = Vue.createApp({
  template: `
    <el-container id="app-shell" class="app-shell" :class="{ collapsed: sidebarCollapsed }">
      <el-aside class="aside" :width="sidebarCollapsed ? '72px' : '236px'">
        <div class="brand-panel">
          <div class="brand-mark">SI</div>
          <div class="brand-copy" v-show="!sidebarCollapsed">
            <strong>StockInsight</strong>
            <span>股票分析平台</span>
          </div>
        </div>
        <el-menu class="sidebar-menu" :default-active="routeName" :collapse="sidebarCollapsed" @select="navigate">
          <el-menu-item index="market"><span class="nav-glyph">▧</span><template #title>行情中心</template></el-menu-item>
          <el-menu-item index="watchlist"><span class="nav-glyph">☆</span><template #title>自选观察</template></el-menu-item>
          <el-menu-item index="screener"><span class="nav-glyph">⌕</span><template #title>选股器</template></el-menu-item>
          <el-menu-item index="sectors"><span class="nav-glyph">▦</span><template #title>板块指数</template></el-menu-item>
          <el-menu-item index="backtest"><span class="nav-glyph">↗</span><template #title>策略回测</template></el-menu-item>
          <el-menu-item index="data-center"><span class="nav-glyph">▤</span><template #title>数据中心</template></el-menu-item>
          <el-menu-item index="sync"><span class="nav-glyph">↻</span><template #title>数据同步</template></el-menu-item>
          <el-menu-item index="settings"><span class="nav-glyph">⚙</span><template #title>系统设置</template></el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-button text class="collapse-btn" @click="toggleSidebar">☰</el-button>
            <div><h1>{{ pageTitle }}</h1><p>{{ pageSubtitle }}</p></div>
          </div>
          <div class="header-right">
            <el-input id="global-search" v-model="searchKeyword" class="global-search" clearable placeholder="股票搜索：输入代码或名称" @keyup.enter="searchAndOpen">
              <template #prefix>⌕</template>
            </el-input>
            <el-tag :type="apiOnline ? 'success' : 'danger'" effect="light">{{ apiOnline ? 'API 在线' : 'API 异常' }}</el-tag>
            <el-button @click="refreshCurrent">刷新</el-button>
          </div>
        </el-header>

        <el-main class="main" id="view-root" v-loading="loading">
          <section v-if="routeName === 'market'" class="view market-view">
            <el-card class="page-header hero-market">
              <div><h2>行情中心</h2><p>市场概览、股票搜索和本地可分析数据状态。</p></div>
              <div class="hero-actions">
                <el-statistic title="最新交易日" :value="latestTradeDate" />
                <el-statistic title="可分析股票" :value="readiness.updated_symbols || 0" />
              </div>
            </el-card>
            <el-row :gutter="16" class="v2-market-panels">
              <el-col :span="8"><el-card class="glass-card"><template #header>指数概览</template><el-empty v-if="!marketDashboard.indexes.length" description="暂无指数快照" /><el-table v-else :data="marketDashboard.indexes" height="240"><el-table-column prop="name" label="名称" /><el-table-column prop="price" label="点位" align="right" :formatter="numberFormatter" /><el-table-column prop="change_rate" label="涨跌幅" align="right" :formatter="percentColumnFormatter" /></el-table></el-card></el-col>
              <el-col :span="8"><el-card class="glass-card"><template #header>板块热度</template><el-empty v-if="!marketDashboard.sectors.length" description="暂无板块快照" /><el-table v-else :data="marketDashboard.sectors" height="240"><el-table-column prop="name" label="板块" /><el-table-column prop="change_rate" label="涨跌幅" align="right" :formatter="percentColumnFormatter" /></el-table></el-card></el-col>
              <el-col :span="8"><el-card class="glass-card"><template #header>数据新鲜度</template><el-descriptions :column="1" border><el-descriptions-item label="最新交易日">{{ marketDashboard.freshness.latest_trade_date || latestTradeDate }}</el-descriptions-item><el-descriptions-item label="可分析股票">{{ formatInt(marketDashboard.freshness.updated_symbols || readiness.updated_symbols) }}</el-descriptions-item><el-descriptions-item label="总股票">{{ formatInt(marketDashboard.freshness.expected_symbols || readiness.expected_symbols) }}</el-descriptions-item><el-descriptions-item label="分析就绪">{{ marketDashboard.freshness.ready_for_analysis ? '是' : '否' }}</el-descriptions-item></el-descriptions></el-card></el-col>
            </el-row>
            <el-alert class="market-source-alert" type="info" show-icon :closable="false" :title="marketDataStatusText" />
            <el-row :gutter="16" class="market-rank-row">
              <el-col :span="8"><el-card class="glass-card"><template #header>涨幅榜</template><el-empty v-if="!marketDashboard.rankings.gainers.length" description="暂无涨幅排行" /><el-table v-else :data="marketDashboard.rankings.gainers" height="260" @row-dblclick="handleStockRowDblClick"><el-table-column prop="symbol" label="代码" width="105" /><el-table-column prop="name" label="名称" /><el-table-column prop="price" label="现价" width="86" align="right" :formatter="numberFormatter" /><el-table-column prop="change_rate" label="涨幅" width="90" align="right" :formatter="percentColumnFormatter" /></el-table></el-card></el-col>
              <el-col :span="8"><el-card class="glass-card"><template #header>跌幅榜</template><el-empty v-if="!marketDashboard.rankings.losers.length" description="暂无跌幅排行" /><el-table v-else :data="marketDashboard.rankings.losers" height="260" @row-dblclick="handleStockRowDblClick"><el-table-column prop="symbol" label="代码" width="105" /><el-table-column prop="name" label="名称" /><el-table-column prop="price" label="现价" width="86" align="right" :formatter="numberFormatter" /><el-table-column prop="change_rate" label="跌幅" width="90" align="right" :formatter="percentColumnFormatter" /></el-table></el-card></el-col>
              <el-col :span="8"><el-card class="glass-card"><template #header>成交额榜</template><el-empty v-if="!marketDashboard.rankings.amount.length" description="暂无成交额排行" /><el-table v-else :data="marketDashboard.rankings.amount" height="260" @row-dblclick="handleStockRowDblClick"><el-table-column prop="symbol" label="代码" width="105" /><el-table-column prop="name" label="名称" /><el-table-column prop="amount" label="成交额" align="right" :formatter="largeNumberFormatter" /><el-table-column prop="change_rate" label="涨跌幅" width="90" align="right" :formatter="percentColumnFormatter" /></el-table></el-card></el-col>
            </el-row>
            <el-card class="glass-card">
              <template #header>
                <div class="card-header">
                  <span>市场概览</span>
                  <el-button-group>
                    <el-button :type="marketTab === 'index' ? 'primary' : ''" @click="marketTab = 'index'">指数</el-button>
                    <el-button :type="marketTab === 'sector' ? 'primary' : ''" @click="marketTab = 'sector'">板块</el-button>
                    <el-button :type="marketTab === 'stock' ? 'primary' : ''" @click="marketTab = 'stock'">个股</el-button>
                  </el-button-group>
                </div>
              </template>
              <div v-if="marketTab === 'index'" class="metric-strip">
                <div class="metric-tile up"><span>可分析股票</span><strong>{{ formatInt(readiness.updated_symbols) }}</strong><small>{{ formatInt(readiness.expected_symbols) }} 总股票</small></div>
                <div class="metric-tile"><span>分析日线</span><strong>{{ formatInt(analysisRows) }}</strong><small>最新交易日覆盖</small></div>
                <div class="metric-tile" :class="readiness.missing_symbol_count ? 'down' : 'up'"><span>缺失股票</span><strong>{{ formatInt(readiness.missing_symbol_count) }}</strong><small>需要补齐</small></div>
                <div class="metric-tile" :class="schedulerRunning ? 'up' : 'down'"><span>同步调度</span><strong>{{ schedulerRunning ? '运行中' : '未运行' }}</strong><small>每日 {{ settings.sync_time || '-' }}</small></div>
              </div>
              <el-table v-else-if="marketTab === 'sector'" :data="industryGroups" height="420">
                <el-table-column prop="name" label="板块名称" />
                <el-table-column prop="count" label="股票数" width="120" align="right" />
                <el-table-column prop="examples" label="样例股票"><template #default="{ row }">{{ row.examples.join(', ') }}</template></el-table-column>
              </el-table>
              <el-table v-else :data="filteredStocks.slice(0, 80)" height="460" @row-dblclick="handleStockRowDblClick">
                <el-table-column prop="symbol" label="代码" width="130"><template #default="{ row }"><el-button link type="primary" @click="navigateToStock(row.symbol)">{{ row.symbol }}</el-button></template></el-table-column>
                <el-table-column prop="name" label="名称" width="140" />
                <el-table-column prop="exchange" label="市场" width="90" />
                <el-table-column prop="industry" label="行业" min-width="160" />
                <el-table-column prop="source" label="来源" width="100" />
              </el-table>
            </el-card>
          </section>

          <section v-else-if="routeName === 'watchlist'" class="view">
            <el-card class="page-header"><h2>自选观察</h2><p>重点跟踪最近关注的股票，点击进入详情。</p></el-card>
            <el-card class="glass-card">
              <template #header><div class="card-header"><span>观察列表</span><span class="muted">{{ watchlistStocks.length }} 只</span></div></template>
              <div class="watch-chip-list">
                <button v-for="stock in watchlistStocks" :key="stock.symbol" class="watch-chip" @click="navigateToStock(stock.symbol)"><strong>{{ stock.symbol }}</strong><span>{{ stock.name || '-' }}</span></button>
              </div>
            </el-card>
          </section>

          <section v-else-if="routeName === 'screener'" class="view">
            <el-card class="page-header"><h2>选股器</h2><p>左侧设置筛选条件，右侧查看候选股票。</p></el-card>
            <el-row :gutter="20">
              <el-col :span="6"><el-card class="condition-panel"><template #header>筛选条件</template>
                <el-form label-position="top">
                  <el-form-item label="交易日期"><el-date-picker v-model="screenerForm.trade_date" value-format="YYYY-MM-DD" type="date" style="width:100%" /></el-form-item>
                  <el-form-item label="股票范围"><el-input v-model="screenerForm.symbols" placeholder="留空为全量，或输入代码" /></el-form-item>
                  <el-form-item label="信号类型"><el-select v-model="screenerForm.signal_filter" style="width:100%"><el-option label="全部信号" value="all" /><el-option label="偏买入" value="buy_like" /><el-option label="风险降低" value="risk_reduction" /><el-option label="上升趋势" value="trend_up" /></el-select></el-form-item>
                  <el-form-item label="价格模式"><el-select v-model="screenerForm.price_mode" style="width:100%"><el-option label="前复权" value="forward_adjusted" /><el-option label="不复权" value="unadjusted" /></el-select></el-form-item>
                  <el-button type="primary" style="width:100%" :loading="screenerLoading" @click="runScreener">开始选股</el-button>
                </el-form>
              </el-card></el-col>
              <el-col :span="18"><el-card class="result-panel"><template #header><div class="card-header"><span>选股结果</span><span class="muted">{{ screeningResults.length }} 只</span></div></template>
                <el-table :data="screeningResults" height="580" @row-dblclick="handleStockRowDblClick">
                  <el-table-column prop="symbol" label="代码" width="130"><template #default="{ row }"><el-button link type="primary" @click="navigateToStock(row.symbol)">{{ row.symbol }}</el-button></template></el-table-column>
                  <el-table-column prop="name" label="名称" width="140" />
                  <el-table-column prop="trade_date" label="日期" width="120" />
                  <el-table-column prop="close" label="收盘" width="100" align="right" :formatter="numberFormatter" />
                  <el-table-column prop="expma17" label="EXPMA17" width="110" align="right" :formatter="numberFormatter" />
                  <el-table-column prop="expma50" label="EXPMA50" width="110" align="right" :formatter="numberFormatter" />
                  <el-table-column prop="selected_signal" label="信号" width="120" :formatter="signalFormatter" />
                  <el-table-column prop="trend_state" label="趋势" min-width="140" :formatter="trendFormatter" />
                </el-table>
              </el-card></el-col>
            </el-row>
          </section>

          <section v-else-if="routeName === 'backtest'" class="view">
            <el-card class="page-header"><h2>策略回测</h2><p>配置策略参数，查看收益、最大回撤和交易明细。</p></el-card>
            <el-row :gutter="20">
              <el-col :span="6"><el-card class="condition-panel"><template #header>回测配置</template>
                <el-form label-position="top">
                  <el-form-item label="策略名称"><el-select v-model="backtestForm.strategy" style="width:100%"><el-option label="EXPMA17/50 趋势回调" value="expma_17_50" /></el-select></el-form-item>
                  <el-form-item label="股票范围"><el-input v-model="backtestForm.symbols" placeholder="留空为全量，或输入代码" /></el-form-item>
                  <el-form-item label="开始日期"><el-date-picker v-model="backtestForm.start_date" value-format="YYYY-MM-DD" type="date" style="width:100%" /></el-form-item>
                  <el-form-item label="结束日期"><el-date-picker v-model="backtestForm.end_date" value-format="YYYY-MM-DD" type="date" style="width:100%" /></el-form-item>
                  <el-form-item label="初始资金"><el-input-number v-model="backtestForm.initial_capital" :min="1" style="width:100%" /></el-form-item>
                  <el-button type="primary" style="width:100%" :loading="backtestLoading" @click="runBacktest">开始回测</el-button>
                </el-form>
              </el-card></el-col>
              <el-col :span="18"><el-card class="result-panel"><template #header><div class="card-header"><span>回测结果</span><el-button :disabled="!backtest.summary" @click="exportBacktestReport">导出报告</el-button></div></template>
                <div v-if="backtest.summary" class="metric-strip">
                  <div class="metric-tile"><span>最终权益</span><strong>{{ formatNumber(backtest.summary.final_equity) }}</strong><small>初始 {{ formatNumber(backtest.summary.initial_capital) }}</small></div>
                  <div class="metric-tile" :class="backtest.summary.total_return >= 0 ? 'up' : 'down'"><span>总收益</span><strong>{{ formatPercent(backtest.summary.total_return) }}</strong><small>策略收益</small></div>
                  <div class="metric-tile down"><span>最大回撤</span><strong>{{ formatPercent(backtest.summary.max_drawdown) }}</strong><small>风险指标</small></div>
                  <div class="metric-tile"><span>交易次数</span><strong>{{ formatInt(backtest.summary.trade_count) }}</strong><small>成交记录</small></div>
                </div>
                <div id="equity-chart" class="kline-chart"></div>
                <el-table :data="backtest.trades || []" height="260" style="margin-top:16px">
                  <el-table-column prop="symbol" label="代码" width="120" />
                  <el-table-column prop="signal_date" label="信号日期" width="120" />
                  <el-table-column prop="trade_date" label="执行日期" width="120" />
                  <el-table-column prop="signal" label="信号" width="110" :formatter="signalFormatter" />
                  <el-table-column prop="price" label="价格" width="100" align="right" :formatter="numberFormatter" />
                </el-table>
              </el-card></el-col>
            </el-row>
          </section>

          <section v-else-if="routeName === 'sectors'" class="view">
            <el-card class="page-header"><h2>板块指数</h2><p>查看指数、板块和成分股数据覆盖情况。</p></el-card>
            <el-row :gutter="20">
              <el-col :span="12"><el-card class="glass-card"><template #header>指数</template><el-empty v-if="!marketDashboard.indexes.length" description="暂无指数数据" /><el-table v-else :data="marketDashboard.indexes" height="420"><el-table-column prop="name" label="名称" /><el-table-column prop="index_code" label="代码" /></el-table></el-card></el-col>
              <el-col :span="12"><el-card class="glass-card"><template #header>板块</template><el-empty v-if="!marketDashboard.sectors.length" description="暂无板块数据" /><el-table v-else :data="marketDashboard.sectors" height="420"><el-table-column prop="name" label="名称" /><el-table-column prop="sector_code" label="代码" /></el-table></el-card></el-col>
            </el-row>
          </section>

          <section v-else-if="routeName === 'stock'" class="view stock-detail-view">
            <el-card class="stock-header glass-card">
              <div class="stock-basic"><h2>{{ selectedStock.name || selectedStock.symbol }} <span class="stock-code">({{ selectedStock.symbol }})</span></h2><div class="stock-tags"><el-tag>{{ selectedStock.exchange || '-' }}</el-tag><el-tag type="info">{{ selectedStock.industry || '未分类' }}</el-tag><el-tag :type="latestBar.data_quality === 'ok' ? 'success' : 'warning'">{{ qualityLabel(latestBar.data_quality) }}</el-tag></div></div>
              <div class="stock-price"><div class="current-price">{{ formatNumber(latestBar.close) }}</div><div class="price-change">最新交易日 {{ latestBar.trade_date || '-' }}</div><el-button @click="addToWatchlist(selectedStock.symbol)">加入自选</el-button></div>
            </el-card>
            <el-row :gutter="20" class="stock-detail-grid">
              <el-col :span="16"><el-card><template #header><div class="card-header"><span>K线图</span><el-radio-group size="small" v-model="klinePeriod" @change="renderKlineChart"><el-radio-button label="day">日线</el-radio-button><el-radio-button label="week">周线</el-radio-button><el-radio-button label="month">月线</el-radio-button></el-radio-group></div></template><div id="kline-chart" class="kline-chart"></div></el-card></el-col>
              <el-col :span="8"><el-card><template #header>基本信息</template><el-descriptions :column="1" border><el-descriptions-item label="开盘">{{ formatNumber(latestBar.open) }}</el-descriptions-item><el-descriptions-item label="最高">{{ formatNumber(latestBar.high) }}</el-descriptions-item><el-descriptions-item label="最低">{{ formatNumber(latestBar.low) }}</el-descriptions-item><el-descriptions-item label="收盘">{{ formatNumber(latestBar.close) }}</el-descriptions-item><el-descriptions-item label="成交量">{{ formatInt(latestBar.volume) }}</el-descriptions-item><el-descriptions-item label="价格模式">{{ priceModeLabel(latestBar.price_mode) }}</el-descriptions-item></el-descriptions></el-card></el-col>
              <el-col :span="12"><el-card><template #header>策略信号</template><el-table :data="stockSignals.slice(-20).reverse()" height="320"><el-table-column prop="trade_date" label="日期" /><el-table-column prop="selected_signal" label="信号" :formatter="signalFormatter" /><el-table-column prop="trend_state" label="趋势" :formatter="trendFormatter" /></el-table></el-card></el-col>
              <el-col :span="12"><el-card><template #header>最近日线</template><el-table :data="stockBars.slice(-40).reverse()" height="320"><el-table-column prop="trade_date" label="日期" /><el-table-column prop="close" label="收盘" align="right" :formatter="numberFormatter" /><el-table-column prop="data_quality" label="质量" :formatter="qualityFormatter" /></el-table></el-card></el-col>
              <el-col :span="24"><el-card><template #header>企业研究</template><el-tabs v-model="stockEnterpriseActiveTab" @tab-change="handleEnterpriseTabChange" @tab-click="handleEnterpriseTabChange">
                <el-tab-pane label="财务三表" name="financials"><el-descriptions :column="4" border class="enterprise-summary"><el-descriptions-item label="最新报告期">{{ stockFinancials.summary?.latest_report_date || '-' }}</el-descriptions-item><el-descriptions-item label="利润表">{{ formatInt(stockFinancials.summary?.income_rows) }}</el-descriptions-item><el-descriptions-item label="资产负债表">{{ formatInt(stockFinancials.summary?.balance_rows) }}</el-descriptions-item><el-descriptions-item label="现金流量表">{{ formatInt(stockFinancials.summary?.cashflow_rows) }}</el-descriptions-item></el-descriptions><el-tabs><el-tab-pane label="利润表"><el-table :data="stockFinancials.income || []" height="280"><el-table-column prop="report_date" label="报告期" /><el-table-column prop="revenue" label="营收" align="right" :formatter="numberFormatter" /><el-table-column prop="net_profit" label="净利润" align="right" :formatter="numberFormatter" /></el-table></el-tab-pane><el-tab-pane label="资产负债"><el-table :data="stockFinancials.balance || []" height="280"><el-table-column prop="report_date" label="报告期" /><el-table-column prop="total_assets" label="资产" align="right" :formatter="numberFormatter" /><el-table-column prop="total_liabilities" label="负债" align="right" :formatter="numberFormatter" /></el-table></el-tab-pane><el-tab-pane label="现金流"><el-table :data="stockFinancials.cashflow || []" height="280"><el-table-column prop="report_date" label="报告期" /><el-table-column prop="net_operating_cashflow" label="经营现金流" align="right" :formatter="numberFormatter" /></el-table></el-tab-pane></el-tabs></el-tab-pane>
                <el-tab-pane label="企业资料" name="profile"><el-empty v-if="!stockOverview.company_profile" description="暂无公司资料" /><el-descriptions v-else :column="2" border><el-descriptions-item label="机构名称">{{ stockOverview.company_profile.company_name || '-' }}</el-descriptions-item><el-descriptions-item label="行业">{{ stockOverview.company_profile.industry || '-' }}</el-descriptions-item><el-descriptions-item label="地区">{{ stockOverview.company_profile.region || '-' }}</el-descriptions-item><el-descriptions-item label="成立日期">{{ stockOverview.company_profile.found_date || '-' }}</el-descriptions-item><el-descriptions-item label="董事长">{{ stockOverview.company_profile.chairman || '-' }}</el-descriptions-item><el-descriptions-item label="总裁">{{ stockOverview.company_profile.president || '-' }}</el-descriptions-item><el-descriptions-item label="法定代表人">{{ stockOverview.company_profile.legal_person || '-' }}</el-descriptions-item><el-descriptions-item label="董秘">{{ stockOverview.company_profile.secretary || '-' }}</el-descriptions-item><el-descriptions-item label="注册资本">{{ formatLargeNumber(stockOverview.company_profile.registered_capital) }}</el-descriptions-item><el-descriptions-item label="员工数量">{{ formatInt(stockOverview.company_profile.employee_count) }}</el-descriptions-item><el-descriptions-item label="会计师事务所">{{ stockOverview.company_profile.accounting_firm || '-' }}</el-descriptions-item><el-descriptions-item label="法律顾问">{{ stockOverview.company_profile.legal_adviser || '-' }}</el-descriptions-item><el-descriptions-item label="电话">{{ stockOverview.company_profile.org_tel || '-' }}</el-descriptions-item><el-descriptions-item label="邮箱">{{ stockOverview.company_profile.org_email || '-' }}</el-descriptions-item><el-descriptions-item label="网站">{{ stockOverview.company_profile.org_web || '-' }}</el-descriptions-item><el-descriptions-item label="地址">{{ stockOverview.company_profile.address || '-' }}</el-descriptions-item><el-descriptions-item label="主营业务" :span="2">{{ stockOverview.company_profile.main_business || '-' }}</el-descriptions-item><el-descriptions-item label="公司简介" :span="2">{{ stockOverview.company_profile.company_profile || stockOverview.company_profile.org_profile || stockOverview.company_profile.description || '-' }}</el-descriptions-item></el-descriptions></el-tab-pane>
                <el-tab-pane label="股东高管" name="people"><el-tabs><el-tab-pane label="十大股东"><el-empty v-if="!stockOverview.holders.length" description="暂无十大股东" /><el-table v-else :data="stockOverview.holders" height="300"><el-table-column prop="report_date" label="报告期" width="110" /><el-table-column prop="holder_rank" label="排名" width="70" align="right" /><el-table-column prop="holder_name" label="股东名称" /><el-table-column prop="shareholding_amount" label="持股数" align="right" :formatter="largeNumberFormatter" /><el-table-column prop="shareholding_ratio" label="持股比例" align="right" :formatter="percentColumnFormatter" /></el-table></el-tab-pane><el-tab-pane label="董监高"><el-empty v-if="!stockOverview.officers.length" description="暂无董监高" /><el-table v-else :data="stockOverview.officers" height="300"><el-table-column prop="officer_name" label="姓名" /><el-table-column prop="title" label="职务" /><el-table-column prop="gender" label="性别" width="80" /><el-table-column prop="age" label="年龄" width="80" align="right" /><el-table-column prop="term_start_date" label="任期开始" /></el-table></el-tab-pane><el-tab-pane label="薪酬持股"><el-empty v-if="!stockOverview.officer_rewards.length" description="暂无薪酬持股" /><el-table v-else :data="stockOverview.officer_rewards" height="300"><el-table-column prop="report_date" label="报告期" /><el-table-column prop="officer_name" label="姓名" /><el-table-column prop="title" label="职务" /><el-table-column prop="reward" label="薪酬" align="right" :formatter="largeNumberFormatter" /><el-table-column prop="hold_volume" label="持股数" align="right" :formatter="largeNumberFormatter" /></el-table></el-tab-pane></el-tabs></el-tab-pane>
                <el-tab-pane label="分红股本" name="capital" data-copy="分红与股本"><el-tabs><el-tab-pane label="分红送配"><el-empty v-if="!stockOverview.corporate_actions.length" description="暂无分红送配" /><el-table v-else :data="stockOverview.corporate_actions" height="300"><el-table-column prop="notice_date" label="公告日" /><el-table-column prop="action_type" label="类型" /><el-table-column prop="dividend" label="分红" align="right" :formatter="numberFormatter" /><el-table-column prop="ex_dividend_date" label="除权日" /></el-table></el-tab-pane><el-tab-pane label="股本历史"><el-empty v-if="!stockOverview.share_capital.length" description="暂无股本历史" /><el-table v-else :data="stockOverview.share_capital" height="300"><el-table-column prop="end_date" label="日期" /><el-table-column prop="total_shares" label="总股本" align="right" :formatter="largeNumberFormatter" /><el-table-column prop="floating_shares" label="流通股本" align="right" :formatter="largeNumberFormatter" /></el-table></el-tab-pane></el-tabs></el-tab-pane>
                <el-tab-pane label="资金流" name="moneyflow"><el-descriptions :column="2" border class="enterprise-summary"><el-descriptions-item label="最新交易日">{{ stockCapitalFlow.summary?.latest_trade_date || '-' }}</el-descriptions-item><el-descriptions-item label="记录数">{{ formatInt(stockCapitalFlow.summary?.rows) }}</el-descriptions-item></el-descriptions><el-empty v-if="!stockCapitalFlow.rows.length" description="暂无资金流数据" /><el-table v-else :data="stockCapitalFlow.rows" height="300"><el-table-column prop="trade_date" label="日期" /><el-table-column prop="main_net_inflow_amount" label="主力净流入" align="right" :formatter="largeNumberFormatter" /><el-table-column prop="main_net_ratio" label="净比" align="right" :formatter="percentColumnFormatter" /></el-table></el-tab-pane>
                <el-tab-pane label="数据状态" name="status"><el-descriptions :column="2" border><el-descriptions-item label="公司资料">{{ enterpriseModuleStatusLabel('company_profile') }} / {{ formatInt(enterpriseModuleStatus('company_profile').rows) }}</el-descriptions-item><el-descriptions-item label="分红送配">{{ enterpriseModuleStatusLabel('corporate_actions') }} / {{ formatInt(enterpriseModuleStatus('corporate_actions').rows) }}</el-descriptions-item><el-descriptions-item label="股本历史">{{ enterpriseModuleStatusLabel('share_capital') }} / {{ formatInt(enterpriseModuleStatus('share_capital').rows) }}</el-descriptions-item><el-descriptions-item label="十大股东">{{ enterpriseModuleStatusLabel('holders') }} / {{ formatInt(enterpriseModuleStatus('holders').rows) }}</el-descriptions-item><el-descriptions-item label="董监高">{{ enterpriseModuleStatusLabel('officers') }} / {{ formatInt(enterpriseModuleStatus('officers').rows) }}</el-descriptions-item><el-descriptions-item label="薪酬持股">{{ enterpriseModuleStatusLabel('officer_rewards') }} / {{ formatInt(enterpriseModuleStatus('officer_rewards').rows) }}</el-descriptions-item><el-descriptions-item label="资金流">{{ enterpriseModuleStatusLabel('capital_flow') }} / {{ formatInt(enterpriseModuleStatus('capital_flow').rows) }}</el-descriptions-item></el-descriptions></el-tab-pane>
              </el-tabs></el-card></el-col>
            </el-row>
          </section>

          <section v-else-if="routeName === 'data-center'" class="view">
            <el-card class="page-header"><h2>数据中心</h2><p>查看底层数据覆盖率、研究数据状态和同步任务健康度。</p></el-card>
            <el-row :gutter="20">
              <el-col :span="8"><el-card class="glass-card"><template #header>核心行情</template><el-descriptions :column="1" border><el-descriptions-item label="分析日线">{{ formatInt(dataCenterCoverage.core?.analysis_daily_bars?.rows) }}</el-descriptions-item><el-descriptions-item label="最新交易日">{{ dataCenterCoverage.sync?.readiness?.latest_trade_date || '-' }}</el-descriptions-item><el-descriptions-item label="缺失股票">{{ formatInt(dataCenterCoverage.sync?.readiness?.missing_symbol_count) }}</el-descriptions-item></el-descriptions></el-card></el-col>
              <el-col :span="8"><el-card class="glass-card"><template #header>研究数据</template><el-descriptions :column="1" border><el-descriptions-item label="财务报表">{{ formatInt(dataCenterCoverage.research?.financial_statements?.rows) }}</el-descriptions-item><el-descriptions-item label="资金流">{{ formatInt(dataCenterCoverage.research?.capital_flow?.rows) }}</el-descriptions-item><el-descriptions-item label="公司资料">{{ formatInt(dataCenterCoverage.research?.company_profiles?.rows) }}</el-descriptions-item><el-descriptions-item label="分红送配">{{ formatInt(dataCenterCoverage.research?.corporate_actions?.rows) }}</el-descriptions-item><el-descriptions-item label="股本历史">{{ formatInt(dataCenterCoverage.research?.share_capital?.rows) }}</el-descriptions-item><el-descriptions-item label="十大股东">{{ formatInt(dataCenterCoverage.research?.holders?.rows) }}</el-descriptions-item><el-descriptions-item label="董监高">{{ formatInt(dataCenterCoverage.research?.officers?.rows) }}</el-descriptions-item><el-descriptions-item label="薪酬持股">{{ formatInt(dataCenterCoverage.research?.officer_rewards?.rows) }}</el-descriptions-item></el-descriptions></el-card></el-col>
              <el-col :span="8"><el-card class="glass-card"><template #header>市场结构</template><el-descriptions :column="1" border><el-descriptions-item label="指数">{{ formatInt(dataCenterCoverage.market_structure?.indexes?.rows) }}</el-descriptions-item><el-descriptions-item label="板块">{{ formatInt(dataCenterCoverage.market_structure?.sectors?.rows) }}</el-descriptions-item><el-descriptions-item label="成分股">{{ formatInt((dataCenterCoverage.market_structure?.index_constituents?.rows || 0) + (dataCenterCoverage.market_structure?.sector_constituents?.rows || 0)) }}</el-descriptions-item></el-descriptions></el-card></el-col>
              <el-col :span="24"><el-card class="glass-card"><template #header>V2 数据刷新</template><el-button type="primary" :loading="syncLoading" @click="runFundamentalRefresh">刷新当前股票研究数据</el-button><el-button :loading="syncLoading" @click="runMarketStructureSync">刷新指数与板块结构</el-button></el-card></el-col>
            </el-row>
          </section>

          <section v-else-if="routeName === 'sync'" class="view">
            <el-card class="page-header"><h2>数据同步</h2><p>每日 0 点同步前一日数据，失败股票支持失败重试。</p></el-card>
            <el-row :gutter="20">
              <el-col :span="8"><el-card class="glass-card"><template #header>自动同步</template><el-descriptions :column="1" border><el-descriptions-item label="同步时间">{{ settings.sync_time }}</el-descriptions-item><el-descriptions-item label="失败重试">{{ settings.sync_retry_rounds }} 轮</el-descriptions-item><el-descriptions-item label="重试并发">{{ settings.sync_retry_max_workers }}</el-descriptions-item><el-descriptions-item label="缺失股票">{{ readiness.missing_symbol_count }}</el-descriptions-item></el-descriptions></el-card></el-col>
              <el-col :span="16"><el-card class="glass-card"><template #header>手动同步</template><el-form inline><el-form-item><el-input v-model="syncForm.symbols" placeholder="留空为全量，或输入股票代码" /></el-form-item><el-form-item><el-date-picker v-model="syncForm.start_date" value-format="YYYY-MM-DD" type="date" placeholder="开始日期" /></el-form-item><el-form-item><el-date-picker v-model="syncForm.end_date" value-format="YYYY-MM-DD" type="date" placeholder="结束日期" /></el-form-item><el-form-item><el-button type="primary" :loading="syncLoading" @click="runManualSync">开始同步</el-button></el-form-item></el-form></el-card></el-col>
              <el-col :span="24"><el-card class="glass-card"><template #header><div class="card-header"><span>同步任务与失败重试</span><el-button @click="refreshCurrent">重新加载</el-button></div></template><el-table :data="jobs" height="460"><el-table-column prop="id" label="ID" width="90" /><el-table-column prop="job_type" label="类型" :formatter="jobTypeFormatter" /><el-table-column prop="status" label="状态" :formatter="statusFormatter" width="120" /><el-table-column prop="requested_by" label="来源" width="140" /><el-table-column label="成功" width="90" align="right"><template #default="{ row }">{{ itemSuccess(row) }}</template></el-table-column><el-table-column label="失败" width="90" align="right"><template #default="{ row }">{{ itemFailed(row) }}</template></el-table-column><el-table-column label="操作" width="120"><template #default="{ row }"><el-button v-if="itemFailed(row)" link type="primary" @click="retryJob(row.id)">失败重试</el-button></template></el-table-column></el-table></el-card></el-col>
            </el-row>
          </section>

          <section v-else-if="routeName === 'settings'" class="view">
            <el-card class="page-header"><h2>系统设置</h2><p>当前运行服务、数据源和调度参数。</p></el-card>
            <el-row :gutter="20">
              <el-col :span="8"><el-card><template #header>数据库</template><el-descriptions :column="1" border><el-descriptions-item label="主机">{{ mysql.host }}</el-descriptions-item><el-descriptions-item label="端口">{{ mysql.port }}</el-descriptions-item><el-descriptions-item label="库名">{{ mysql.database }}</el-descriptions-item><el-descriptions-item label="用户">{{ mysql.user }}</el-descriptions-item></el-descriptions></el-card></el-col>
              <el-col :span="8"><el-card><template #header>数据源</template><el-descriptions :column="1" border><el-descriptions-item label="优先级">{{ providerPriority }}</el-descriptions-item><el-descriptions-item label="米筐频率">{{ settings.miana_max_requests_per_minute }} 次/分钟</el-descriptions-item><el-descriptions-item label="Tushare Token">{{ settings.tushare_token_configured ? '已配置' : '未配置' }}</el-descriptions-item><el-descriptions-item label="默认价格">{{ priceModeLabel(settings.default_price_mode) }}</el-descriptions-item></el-descriptions></el-card></el-col>
              <el-col :span="8"><el-card><template #header>调度与重试</template><el-descriptions :column="1" border><el-descriptions-item label="同步启用">{{ settings.sync_enabled ? '是' : '否' }}</el-descriptions-item><el-descriptions-item label="每日时间">{{ settings.sync_time }}</el-descriptions-item><el-descriptions-item label="同步并发">{{ settings.sync_max_workers }}</el-descriptions-item><el-descriptions-item label="失败重试">{{ settings.sync_retry_rounds }} 轮 / {{ settings.sync_retry_max_workers }} 并发</el-descriptions-item></el-descriptions></el-card></el-col>
            </el-row>
          </section>
        </el-main>
      </el-container>
    </el-container>
  `,
  data() {
    return {
      loading: false,
      apiOnline: false,
      sidebarCollapsed: false,
      routeName: "market",
      routeParam: "",
      searchKeyword: "",
      marketTab: "stock",
      health: {},
      settings: {},
      coverage: {},
      readiness: {},
      jobs: [],
      stocks: [],
      selectedStock: {},
      stockBars: [],
      stockIndicators: [],
      stockSignals: [],
      marketDashboard: { indexes: [], sectors: [], rankings: { gainers: [], losers: [], amount: [] }, breadth: {}, freshness: {}, data_source_status: {} },
      marketDashboardLoadedAt: 0,
      marketDashboardCacheTtlMs: 60000,
      stockOverview: { stock: {}, latest_bar: null, company_profile: null, share_capital: [], corporate_actions: [], holders: [], officers: [], officer_rewards: [], data_quality: { enterprise_modules: {} } },
      stockFinancials: { income: [], balance: [], cashflow: [], summary: {} },
      stockCapitalFlow: { rows: [], summary: {} },
      stockEnterpriseActiveTab: "financials",
      dataCenterCoverage: { core: {}, research: {}, market_structure: {}, sync: {} },
      klinePeriod: "day",
      screening: {},
      backtest: {},
      screenerLoading: false,
      backtestLoading: false,
      syncLoading: false,
      screenerForm: {
        trade_date: "",
        symbols: "",
        signal_filter: "all",
        price_mode: "forward_adjusted",
      },
      backtestForm: {
        strategy: "expma_17_50",
        symbols: "",
        start_date: "2024-01-01",
        end_date: "2024-12-31",
        initial_capital: 100000,
        fee_rate: 0.0003,
        slippage_rate: 0.0005,
      },
      syncForm: {
        symbols: "",
        start_date: "",
        end_date: "",
      },
    };
  },

  computed: {
    pageTitle() {
      return {
        market: "行情中心",
        watchlist: "自选观察",
        screener: "选股器",
        sectors: "板块指数",
        backtest: "策略回测",
        stock: "股票详情",
        "data-center": "数据中心",
        sync: "数据同步",
        settings: "系统设置",
      }[this.routeName] || "行情中心";
    },

    pageSubtitle() {
      return {
        market: "实时查看本地股票池、数据覆盖和可分析行情。",
        watchlist: "快速跟踪重点股票的最新日线、信号和数据质量。",
        screener: "使用策略信号和本地分析数据筛选候选股票。",
        sectors: "查看指数、板块、成分股和市场结构数据。",
        backtest: "配置策略参数，查看收益、最大回撤和交易明细。",
        stock: "查看 K线图、EXPMA 指标、信号与数据质量。",
        "data-center": "检查数据覆盖率、研究数据状态和同步任务健康度。",
        sync: "监控每日同步、缺失股票、失败重试和任务历史。",
        settings: "查看数据源、数据库、调度和重试配置。",
      }[this.routeName] || "";
    },

    filteredStocks() {
      const query = String(this.searchKeyword || "").trim().toLowerCase();
      if (!query) return this.stocks;
      return this.stocks.filter((stock) => `${stock.symbol} ${stock.name || ""} ${stock.industry || ""}`.toLowerCase().includes(query));
    },

    industryGroups() {
      const groups = new Map();
      this.stocks.forEach((stock) => {
        const name = stock.industry || "未分类";
        const group = groups.get(name) || { name, count: 0, examples: [] };
        group.count += 1;
        if (group.examples.length < 5) group.examples.push(stock.symbol);
        groups.set(name, group);
      });
      return Array.from(groups.values()).sort((a, b) => b.count - a.count).slice(0, 80);
    },

    watchlistStocks() {
      const saved = JSON.parse(localStorage.getItem("watchlistSymbols") || "[]");
      const symbols = saved.length ? saved : this.stocks.slice(0, 12).map((stock) => stock.symbol);
      return this.stocks.filter((stock) => symbols.includes(stock.symbol));
    },

    latestBar() {
      return this.stockBars[this.stockBars.length - 1] || {};
    },

    latestTradeDate() {
      return this.readiness.latest_trade_date || (this.coverage.analysis_daily_bars || {}).latest_trade_date || "-";
    },

    analysisRows() {
      return (this.coverage.analysis_daily_bars || {}).rows || 0;
    },

    schedulerRunning() {
      return Boolean((this.health.scheduler || {}).running);
    },

    screeningResults() {
      return this.screening.results || [];
    },

    mysql() {
      return this.settings.mysql || {};
    },

    providerPriority() {
      return (this.settings.data_source_priority || []).join(" -> ");
    },

    marketDataStatusText() {
      const status = this.marketDashboard.data_source_status || {};
      if (status.provider === "local") return "行情中心使用本地同步数据；缺失昨日数据时会自动触发一次同步。";
      if (status.provider !== "miana") return "Miana 未配置或未启用，行情中心使用本地分析数据。";
      const stock = status.stock_rankings === "ok" ? "股票排行已接入 Miana" : `股票排行${this.marketStatusLabel(status.stock_rankings)}`;
      const index = status.index_rankings === "ok" ? "指数排行已接入 Miana" : `指数排行${this.marketStatusLabel(status.index_rankings)}`;
      const sector = status.sector_rankings === "ok" ? "板块排行已接入 Miana" : `板块排行${this.marketStatusLabel(status.sector_rankings)}`;
      return `${stock}，${index}，${sector}；全市场实时快照接口当前账号需要企业版权限。`;
    },
  },

  async mounted() {
    window.addEventListener("hashchange", this.loadRoute);
    await this.loadRoute();
  },

  methods: {
    async api(url, options) {
      const response = await fetch(url, options);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`${response.status} ${response.statusText} ${text}`.trim());
      }
      return response.json();
    },

    async loadCoreData() {
      const [health, settings, coverage, readiness, jobsPayload, stocksPayload] = await Promise.all([
        this.api("/api/health"),
        this.api("/api/settings"),
        this.api("/api/sync/coverage"),
        this.api("/api/sync/readiness"),
        this.api("/api/sync/jobs"),
        this.api("/api/stocks"),
      ]);
      this.health = health;
      this.settings = settings;
      this.coverage = coverage;
      this.readiness = readiness;
      this.jobs = jobsPayload.jobs || [];
      this.stocks = stocksPayload.stocks || [];
      this.apiOnline = true;
    },

    async loadRoute(forceRefresh = false) {
      const force = forceRefresh === true;
      const raw = window.location.hash.replace(/^#\//, "") || "market";
      const [name, param] = raw.split("/");
      this.routeName = ["market", "watchlist", "screener", "sectors", "backtest", "stock", "data-center", "sync", "settings"].includes(name) ? name : "market";
      this.routeParam = param || "";
      this.loading = true;
      try {
        await this.loadCoreData();
        if (this.routeName === "market" || this.routeName === "sectors") await this.loadMarketDashboard(force);
        if (this.routeName === "data-center") await this.loadDataCenterCoverage();
        if (this.routeName === "stock") await this.loadStockDetail(this.routeParam || this.stocks[0]?.symbol);
        await nextTick();
        if (this.routeName === "backtest") this.renderEquityChart();
      } catch (error) {
        this.apiOnline = false;
        ElementPlus.ElMessage.error(error.message);
      } finally {
        this.loading = false;
      }
    },

    navigate(route) {
      window.location.hash = `#/${route}`;
    },

    navigateToStock(symbol) {
      if (!symbol) return;
      localStorage.setItem("selectedSymbol", symbol);
      window.location.hash = `#/stock/${encodeURIComponent(symbol)}`;
    },

    handleStockRowDblClick(row) {
      this.navigateToStock(row.symbol);
    },

    searchAndOpen() {
      const match = this.filteredStocks[0];
      if (match) this.navigateToStock(match.symbol);
    },

    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed;
    },

    async refreshCurrent() {
      await this.loadRoute(true);
    },

    async loadStockDetail(symbol) {
      if (!symbol) return;
      const [stock, bars, indicators, signals, overview, financials, capitalFlow] = await Promise.all([
        this.api(`/api/stocks/${encodeURIComponent(symbol)}`),
        this.api(`/api/stocks/${encodeURIComponent(symbol)}/bars?refresh=true`),
        this.api(`/api/stocks/${encodeURIComponent(symbol)}/indicators`),
        this.api(`/api/stocks/${encodeURIComponent(symbol)}/signals`),
        this.loadStockOverview(symbol),
        this.loadStockFinancials(symbol),
        this.loadStockCapitalFlow(symbol),
      ]);
      this.selectedStock = stock || {};
      this.stockBars = bars || [];
      this.stockIndicators = indicators || [];
      this.stockSignals = signals || [];
      this.stockOverview = { stock: {}, latest_bar: null, company_profile: null, share_capital: [], corporate_actions: [], holders: [], officers: [], officer_rewards: [], data_quality: { enterprise_modules: {} }, ...(overview || {}) };
      this.stockFinancials = { income: [], balance: [], cashflow: [], summary: {}, ...(financials || {}) };
      this.stockCapitalFlow = { rows: [], summary: {}, ...(capitalFlow || {}) };
      await nextTick();
      this.renderKlineChart();
    },

    async loadMarketDashboard(force = false) {
      if (!force && this.marketDashboardLoadedAt && Date.now() - this.marketDashboardLoadedAt < this.marketDashboardCacheTtlMs) return;
      this.marketDashboard = await this.api("/api/market/dashboard");
      this.marketDashboardLoadedAt = Date.now();
    },

    async loadDataCenterCoverage() {
      this.dataCenterCoverage = await this.api("/api/data-center/coverage");
    },

    async loadStockOverview(rawSymbol, refreshMissing = false) {
      const symbol = encodeURIComponent(rawSymbol);
      const query = refreshMissing ? "?refresh_missing=true" : "";
      return this.api(`/api/stocks/${symbol}/overview${query}`);
    },

    async handleEnterpriseTabChange(tabName) {
      const selectedTab = typeof tabName === "string" ? tabName : tabName?.paneName || tabName?.props?.name || tabName?.name;
      if (selectedTab !== "people") return;
      const symbol = this.selectedStock.symbol || this.routeParam;
      if (!symbol) return;
      const status = this.enterpriseModuleStatus("officers");
      if (Number(status.rows || 0) > 0) return;
      this.stockOverview = {
        stock: {},
        latest_bar: null,
        company_profile: null,
        share_capital: [],
        corporate_actions: [],
        holders: [],
        officers: [],
        officer_rewards: [],
        data_quality: { enterprise_modules: {} },
        ...(await this.loadStockOverview(symbol, true)),
      };
    },

    async loadStockFinancials(rawSymbol) {
      const symbol = encodeURIComponent(rawSymbol);
      return this.api(`/api/stocks/${symbol}/financials`);
    },

    async loadStockCapitalFlow(rawSymbol) {
      const symbol = encodeURIComponent(rawSymbol);
      return this.api(`/api/stocks/${symbol}/capital-flow`);
    },

    async runScreener() {
      this.screenerLoading = true;
      try {
        const symbols = this.parseSymbols(this.screenerForm.symbols);
        this.screening = await this.api("/api/screenings", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            trade_date: this.screenerForm.trade_date || null,
            symbols: symbols.length ? symbols : null,
            signal_filter: this.screenerForm.signal_filter,
            price_mode: this.screenerForm.price_mode,
          }),
        });
        ElementPlus.ElMessage.success(`选股完成，共 ${this.screening.results?.length || 0} 只`);
      } catch (error) {
        ElementPlus.ElMessage.error(error.message);
      } finally {
        this.screenerLoading = false;
      }
    },

    async runBacktest() {
      this.backtestLoading = true;
      try {
        const symbols = this.parseSymbols(this.backtestForm.symbols);
        this.backtest = await this.api("/api/backtests", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            symbols: symbols.length ? symbols : null,
            start_date: this.backtestForm.start_date,
            end_date: this.backtestForm.end_date,
            initial_capital: Number(this.backtestForm.initial_capital),
            fee_rate: Number(this.backtestForm.fee_rate),
            slippage_rate: Number(this.backtestForm.slippage_rate),
            price_mode: "forward_adjusted",
            allow_partial_coverage: true,
          }),
        });
        ElementPlus.ElMessage.success("回测完成");
        await nextTick();
        this.renderEquityChart();
      } catch (error) {
        ElementPlus.ElMessage.error(error.message);
      } finally {
        this.backtestLoading = false;
      }
    },

    async runManualSync() {
      this.syncLoading = true;
      try {
        const job = await this.api("/api/sync/jobs", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_type: "full_daily_pipeline",
            symbols: this.parseSymbols(this.syncForm.symbols),
            start_date: this.syncForm.start_date || null,
            end_date: this.syncForm.end_date || null,
          }),
        });
        ElementPlus.ElMessage.success(`任务 ${job.id} 已提交`);
        await this.refreshCurrent();
      } catch (error) {
        ElementPlus.ElMessage.error(error.message);
      } finally {
        this.syncLoading = false;
      }
    },

    async retryJob(jobId) {
      try {
        await this.api(`/api/sync/jobs/${encodeURIComponent(jobId)}/retry`, { method: "POST" });
        ElementPlus.ElMessage.success("失败重试任务已提交");
        await this.refreshCurrent();
      } catch (error) {
        ElementPlus.ElMessage.error(error.message);
      }
    },

    async runFundamentalRefresh() {
      this.syncLoading = true;
      try {
        const symbol = this.routeParam || localStorage.getItem("selectedSymbol") || this.stocks[0]?.symbol;
        await this.api("/api/sync/jobs", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ job_type: "fundamental_refresh_pipeline", symbols: symbol ? [symbol] : null }),
        });
        ElementPlus.ElMessage.success("研究数据刷新完成");
        await this.loadDataCenterCoverage();
      } catch (error) {
        ElementPlus.ElMessage.error(error.message);
      } finally {
        this.syncLoading = false;
      }
    },

    async runMarketStructureSync() {
      this.syncLoading = true;
      try {
        await this.api("/api/sync/jobs", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ job_type: "market_structure_pipeline" }),
        });
        ElementPlus.ElMessage.success("市场结构刷新完成");
        await this.loadDataCenterCoverage();
      } catch (error) {
        ElementPlus.ElMessage.error(error.message);
      } finally {
        this.syncLoading = false;
      }
    },

    addToWatchlist(symbol) {
      if (!symbol) return;
      const list = JSON.parse(localStorage.getItem("watchlistSymbols") || "[]");
      if (!list.includes(symbol)) list.unshift(symbol);
      localStorage.setItem("watchlistSymbols", JSON.stringify(list.slice(0, 50)));
      ElementPlus.ElMessage.success("已加入自选观察");
    },

    exportBacktestReport() {
      if (!this.backtest.summary) return;
      const summary = this.backtest.summary;
      const lines = [
        `回测报告 - ${new Date().toLocaleString()}`,
        `最终权益: ${this.formatNumber(summary.final_equity)}`,
        `总收益: ${this.formatPercent(summary.total_return)}`,
        `最大回撤: ${this.formatPercent(summary.max_drawdown)}`,
        `交易次数: ${this.formatInt(summary.trade_count)}`,
      ];
      const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `回测报告_${Date.now()}.txt`;
      link.click();
    },

    renderKlineChart() {
      const el = document.querySelector("#kline-chart");
      if (!el || !window.echarts) return;
      const chart = echarts.init(el);
      const rows = this.aggregateKlineRows(this.stockBars, this.klinePeriod);
      const indicatorMap = new Map(this.stockIndicators.map((item) => [String(item.trade_date), item]));
      const expma17 = this.klinePeriod === "day"
        ? rows.map((row) => Number(indicatorMap.get(String(row.trade_date))?.expma17))
        : this.calculateExpma(rows.map((row) => Number(row.close)), 17);
      const expma50 = this.klinePeriod === "day"
        ? rows.map((row) => Number(indicatorMap.get(String(row.trade_date))?.expma50))
        : this.calculateExpma(rows.map((row) => Number(row.close)), 50);
      const zoomStart = this.zoomStartForRows(rows);
      chart.setOption({
        tooltip: { trigger: "axis", axisPointer: { type: "cross" } },
        legend: { data: ["收盘", "EXPMA17", "EXPMA50"], top: 8 },
        grid: { left: 48, right: 28, top: 54, bottom: 42 },
        xAxis: { type: "category", data: rows.map((row) => row.trade_date), boundaryGap: false },
        yAxis: { type: "value", scale: true, splitLine: { lineStyle: { color: "#edf1f7" } } },
        dataZoom: [{ type: "inside", start: zoomStart, end: 100 }, { type: "slider", start: zoomStart, end: 100, height: 20, bottom: 8 }],
        series: [
          { name: "收盘", type: "line", smooth: true, symbol: "none", data: rows.map((row) => Number(row.close)), lineStyle: { color: "#f56c6c", width: 2 } },
          { name: "EXPMA17", type: "line", smooth: true, symbol: "none", data: expma17, lineStyle: { color: "#409eff", width: 1.6 } },
          { name: "EXPMA50", type: "line", smooth: true, symbol: "none", data: expma50, lineStyle: { color: "#e6a23c", width: 1.6 } },
        ],
      });
    },

    aggregateKlineRows(sourceRows, period) {
      const rows = [...(sourceRows || [])].sort((a, b) => String(a.trade_date).localeCompare(String(b.trade_date)));
      if (period === "day") return rows;

      const groups = new Map();
      rows.forEach((row) => {
        const key = period === "week"
          ? this.weekKey(row.trade_date)
          : period === "month"
            ? String(row.trade_date).slice(0, 7)
            : String(row.trade_date);
        const current = groups.get(key);
        if (!current) {
          groups.set(key, { ...row, volume: Number(row.volume || 0), amount: Number(row.amount || 0) });
          return;
        }
        current.trade_date = row.trade_date;
        current.high = Math.max(Number(current.high), Number(row.high));
        current.low = Math.min(Number(current.low), Number(row.low));
        current.close = row.close;
        current.volume = Number(current.volume || 0) + Number(row.volume || 0);
        current.amount = Number(current.amount || 0) + Number(row.amount || 0);
      });
      return Array.from(groups.values());
    },

    zoomStartForRows(rows) {
      const count = rows.length;
      if (count <= 160) return 0;
      return Math.max(0, Math.round(((count - 160) / count) * 100));
    },

    weekKey(tradeDate) {
      const date = new Date(`${tradeDate}T00:00:00`);
      const day = date.getDay() || 7;
      date.setDate(date.getDate() - day + 1);
      return date.toISOString().slice(0, 10);
    },

    calculateExpma(values, period) {
      const alpha = 2 / (period + 1);
      let previous = null;
      return values.map((value) => {
        if (!Number.isFinite(value)) return null;
        previous = previous === null ? value : alpha * value + (1 - alpha) * previous;
        return Number(previous.toFixed(4));
      });
    },

    renderEquityChart() {
      const el = document.querySelector("#equity-chart");
      if (!el || !window.echarts) return;
      const rows = this.backtest.equity || [];
      const chart = echarts.init(el);
      chart.setOption({
        tooltip: { trigger: "axis" },
        grid: { left: 52, right: 24, top: 28, bottom: 42 },
        xAxis: { type: "category", data: rows.map((row) => row.trade_date), boundaryGap: false },
        yAxis: { type: "value", scale: true, splitLine: { lineStyle: { color: "#edf1f7" } } },
        dataZoom: [{ type: "inside", start: 70, end: 100 }],
        series: [{ name: "权益", type: "line", smooth: true, symbol: "none", areaStyle: { opacity: 0.12 }, data: rows.map((row) => Number(row.equity)), lineStyle: { color: "#409eff", width: 2 } }],
      });
    },

    parseSymbols(value) {
      return String(value || "")
        .split(/[,\s，、]+/)
        .map((item) => item.trim().toUpperCase())
        .filter(Boolean);
    },

    formatNumber(value, digits = 2) {
      if (value === null || value === undefined || value === "") return "-";
      const number = Number(value);
      return Number.isFinite(number) ? number.toFixed(digits) : String(value);
    },

    formatInt(value) {
      const number = Number(value);
      return Number.isFinite(number) ? number.toLocaleString("zh-CN") : "0";
    },

    formatPercent(value) {
      if (value === null || value === undefined || value === "") return "-";
      return `${this.formatNumber(Number(value) * 100, 2)}%`;
    },

    formatLargeNumber(value) {
      const number = Number(value);
      if (!Number.isFinite(number)) return "-";
      if (Math.abs(number) >= 100000000) return `${this.formatNumber(number / 100000000, 2)}亿`;
      if (Math.abs(number) >= 10000) return `${this.formatNumber(number / 10000, 2)}万`;
      return this.formatNumber(number, 2);
    },

    marketStatusLabel(value) {
      return { ok: "已接入", empty: "暂无返回", failed: "请求失败", not_configured: "未配置" }[value] || "状态未知";
    },

    signalLabel(value) {
      return {
        BUY: "买入",
        HALF_SELL: "减半",
        RE_BUY: "回补",
        CLEAR_1: "清仓一",
        CLEAR_2: "清仓二",
        RE_BUY_50: "回踩50回补",
      }[value] || value || "-";
    },

    trendLabel(value) {
      return {
        insufficient: "数据不足",
        above_expma17_expma50: "强势上行",
        trend_up_pullback: "上升回调",
        below_expma50: "跌破EXPMA50",
        neutral: "中性",
      }[value] || value || "-";
    },

    qualityLabel(value) {
      return { ok: "正常", missing_adj_factor: "缺少复权因子" }[value] || value || "-";
    },

    priceModeLabel(value) {
      return { forward_adjusted: "前复权", unadjusted: "不复权" }[value] || value || "-";
    },

    enterpriseModuleStatus(key) {
      return (this.stockOverview.data_quality?.enterprise_modules || {})[key] || { rows: 0, status: "missing", newest_date: null, provider: null };
    },

    enterpriseModuleStatusLabel(key) {
      const status = this.enterpriseModuleStatus(key).status;
      return { synced: "已同步", missing: "暂无数据", failed: "同步失败", stale: "需刷新" }[status] || status || "-";
    },

    statusLabel(value) {
      return { completed: "已完成", completed_with_errors: "部分完成", failed: "失败", pending: "等待中", running: "运行中" }[value] || value || "-";
    },

    jobTypeLabel(value) {
      return { full_daily_pipeline: "全量日线流程", sync_daily_bars: "同步日线", aggregate_daily: "生成分析日线", compute_signals: "计算策略信号" }[value] || value || "-";
    },

    numberFormatter(row, column, value) {
      return this.formatNumber(value);
    },

    largeNumberFormatter(row, column, value) {
      return this.formatLargeNumber(value);
    },

    percentColumnFormatter(row, column, value) {
      return this.formatPercent(value);
    },

    signalFormatter(row, column, value) {
      return this.signalLabel(value);
    },

    trendFormatter(row, column, value) {
      return this.trendLabel(value);
    },

    qualityFormatter(row, column, value) {
      return this.qualityLabel(value);
    },

    statusFormatter(row, column, value) {
      return this.statusLabel(value);
    },

    jobTypeFormatter(row, column, value) {
      return this.jobTypeLabel(value);
    },

    itemSuccess(row) {
      return (row.summary || {}).success || 0;
    },

    itemFailed(row) {
      return (row.summary || {}).failed || 0;
    },
  },
});

app.use(ElementPlus);
app.mount("#app");
