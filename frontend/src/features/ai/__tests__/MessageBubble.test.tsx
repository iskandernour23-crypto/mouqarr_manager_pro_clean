import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import MessageBubble from '../components/MessageBubble';
import { AiMessage } from '../../../store/ai';

describe('MessageBubble', () => {
  it('shows pending badge for offline message', () => {
    const message: AiMessage = {
      id: '1',
      role: 'user',
      content: 'مرحبا',
      createdAt: new Date().toISOString(),
      pending: true,
    };
    render(<MessageBubble message={message} />);
    expect(screen.getByText('قيد الانتظار')).toBeInTheDocument();
  });
});
