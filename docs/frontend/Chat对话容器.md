# Chat 对话容器

## 代码演示

```jsx
import React from 'react';
import Chat, { Bubble, useMessages } from '@chatui/core';

const initialMessages = [
  {
    type: 'system',
    content: { text: 'xx 为您服务' },
  },
  {
    type: 'text',
    content: { text: 'Hi，我是xx，有问题请随时找我哦~' },
    user: {
      avatar: '...url...',
    },
  },
];

// 默认快捷短语，可选
const defaultQuickReplies = [
  {
    icon: 'message',
    name: '联系人工服务',
    isNew: true,
    isHighlight: true,
  },
  {
    name: '短语1',
    isNew: true,
  },
  {
    name: '短语2',
    isHighlight: true,
  },
  {
    name: '短语3',
  },
];

export default function() {
  // 消息列表
  const { messages, appendMsg } = useMessages(initialMessages);

  // 发送回调
  function handleSend(type, val) {
    if (type === 'text' && val.trim()) {
      appendMsg({
        type: 'text',
        content: { text: val },
        position: 'right',
      });

      // TODO: 发送请求
      // 模拟回复消息
      setTimeout(() => {
        appendMsg({
          type: 'text',
          content: { text: '您遇到什么问题啦？请简要描述您的问题~' },
        });
      }, 1000);
    }
  }

  // 快捷短语回调
  function handleQuickReplyClick(item) {
    handleSend('text', item.name);
  }

  function renderMessageContent(msg) {
    const { type, content } = msg;

    // 根据消息类型来渲染
    switch (type) {
      case 'text':
        return <Bubble content={content.text} />;
      case 'image':
        return (
          <Bubble type="image">
            <img src={content.picUrl} alt="" />
          </Bubble>
        );
      default:
        return null;
    }
  }

  return (
    <Chat
      navbar={{ title: '智能助理' }}
      messages={messages}
      renderMessageContent={renderMessageContent}
      quickReplies={defaultQuickReplies}
      onQuickReplyClick={handleQuickReplyClick}
      onSend={handleSend}
    />
  );
}
```

## Props

### Chat

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| wideBreakpoint | string |  | 宽屏断点 |
| navbar | NavbarProps |  | 导航栏配置 |
| renderNavbar | () => ReactNode |  | 导航栏渲染函数，会覆盖 navbar |
| loadMoreText | string |  | 加载更多文案 |
| renderBeforeMessageList | () => ReactNode |  | 在消息列表上面的渲染函数 |
| messagesRef | RefObject<MessageContainerHandle> |  | 消息列表 ref |
| onRefresh | () => Promise<any> |  | 下拉加载回调 |
| onScroll | (event: React.UIEvent<HTMLDivElement, UIEvent>) => void |  | 滚动消息列表回调 |
| messages | MessageProps[] | [] | 消息列表 |
| renderMessageContent | (message: MessageProps) => ReactNode |  | 消息内容渲染函数 |
| quickReplies | QuickReplyItemProps[] |  | 快捷短语列表 |
| quickRepliesVisible | boolean |  | 快捷短语是否可见 |
| onQuickReplyClick | (item: QuickReplyItemProps, index: number) => void |  | 点击快速回复回调 |
| onQuickReplyScroll | () => void |  | 快捷短语的滚动回调 |
| renderQuickReplies | () => ReactNode |  | 快捷短语渲染函数，会覆盖 quickReplies |
| composerRef | RefObject<ComposerHandle> |  | 输入区 ref |
| text | string | '' | 输入框初始内容 |
| placeholder | string | '请输入...' | 输入框占位符 |
| onInputFocus | (event: FocusEvent) => void |  | 输入框聚焦回调 |
| onInputChange | (value: string, event: ChangeEvent) => void |  | 输入框更新回调 |
| onInputBlur | (event: FocusEvent) => void |  | 输入框失去焦点回调 |
| onSend | (type: string, content: string) => void |  | 发送消息回调 |
| onImageSend | (file: File) => Promise<any> |  | 输入框粘贴图片后的回调 |
| inputType | text \| voice | text | 输入方式 |
| onInputTypeChange | (inputType: InputType) => void |  | 输入方式切换回调 |
| recorder | RecorderProps | {} | 语音输入配置 |
| toolbar | ToolbarItemProps[] | [] | 工具栏配置 |
| onToolbarClick | (item: ToolbarItemProps, event: MouseEvent) => void |  | 工具栏点击回调 |
| onAccessoryToggle | (isAccessoryOpen: boolean) => void |  | 工具栏打开/关闭回调 |
| rightAction | IconButtonProps |  | 输入框右边图标按钮配置 |
| Composer | ElementType |  | 输入组件 |

### MessageProps

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| _id | string |  | 消息ID |
| type | string |  | 消息类型 |
| content | Record<string, any> |  | 消息内容 |
| createdAt | number |  | 消息创建时间 |
| user | User | {} | 消息发送者信息 |
| position | 'left' \| 'right' \| 'center' \| 'pop' | 'left' | 消息位置 |
| hasTime | boolean | true | 是否显示时间 |
| status | 'pending' \| 'sent' \| 'fail' |  | 消息状态 |

### ComposerHandle

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| setText | (text: string) => void |  | 设置输入框内容 |

### MessageContainerHandle

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| scrollToEnd | (options?: ScrollToEndOptions) => void |  | 滚动到底部 |

### ScrollToEndOptions

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| animated | boolean |  | 是否平滑滚动 |
| force | boolean |  | 是否强制滚动 |

### QuickReplyItemProps

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| name | string |  | 名称 |
| code | string |  | code |
| icon | string |  | 图标 |
| img | string |  | 图片 |
| isNew | boolean |  | 是否新的 |
| isHighlight | boolean |  | 是否高亮 |