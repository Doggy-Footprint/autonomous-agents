# models.py
# 4단계: 직접 대화, 작업 할당 등 심화된 상호작용 기능 추가

import datetime
import re

class World:
    """시뮬레이션 세계를 정의하고 관리합니다. 프로젝트 상태 보드와 작업 할당 기능이 있습니다."""
    def __init__(self, description="작은 가상 오피스 공간"):
        self.description = description
        self.agents = {}
        self.locations = {"개발팀 자리": [], "휴게실": [], "회의실": []}
        self.project_status = {"로그인 기능": "정상", "결제 기능": "정상"}
        print(f"'{self.description}' 세계가 생성되었습니다.")
        print(f"현재 프로젝트 상태: {self.project_status}")

    def add_agent(self, agent, location):
        if agent.name in self.agents: return
        if location not in self.locations: return
        self.agents[agent.name] = agent
        self.locations[location].append(agent.name)
        agent.location = location
        print(f"'{agent.name}' 에이전트가 '{location}'에 추가되었습니다.")

    def get_location_state(self, location):
        if location not in self.locations: return f"'{location}'은(는) 알 수 없는 장소입니다."
        agent_names = [name for name in self.locations[location]]
        state = f"'{location}'에는 {', '.join(agent_names)}이(가) 있습니다." if agent_names else f"'{location}'에는 아무도 없습니다."
        state += f"\n프로젝트 상태 보드: {self.project_status}"
        return state

    def execute_action(self, agent, action_string):
        print(f"[{agent.name}의 행동 실행] {action_string}")
        # 정규표현식 패턴 확장
        move_match = re.match(r"MOVE to (.*)", action_string, re.IGNORECASE)
        say_match = re.match(r"SAY: (.*)", action_string, re.IGNORECASE)
        say_to_match = re.match(r"SAY to (.*?): (.*)", action_string, re.IGNORECASE)
        do_match = re.match(r"DO: (.*)", action_string, re.IGNORECASE)
        report_match = re.match(r"REPORT BUG: (.*) is (.*)", action_string, re.IGNORECASE)
        fix_match = re.match(r"FIX BUG: (.*)", action_string, re.IGNORECASE)
        assign_match = re.match(r"ASSIGN TASK to (.*?): (.*)", action_string, re.IGNORECASE)

        observation = ""

        if move_match:
            # ... (이전과 동일)
            new_location = move_match.group(1).strip()
            if new_location in self.locations:
                old_location = agent.location
                if agent.name in self.locations[old_location]: self.locations[old_location].remove(agent.name)
                self.locations[new_location].append(agent.name)
                agent.location = new_location
                observation = f"{agent.name}이(가) {old_location}에서 {new_location}(으)로 이동했습니다."
                self.broadcast_observation(agent, observation, public=True)
            else: 
                observation = f"{agent.name}이(가) {new_location}(으)로 이동하려 했지만 실패했습니다."
                agent.add_memory(observation) # 실패한 행동은 자신만 기억

        elif say_to_match: # 직접 대화 먼저 처리
            target_name, message = say_to_match.group(1).strip(), say_to_match.group(2).strip()
            if target_name in self.agents:
                target_agent = self.agents[target_name]
                observation = f"{agent.name}이(가) 당신에게 말합니다: \"{message}\""
                target_agent.add_memory(observation) # 타겟에게만 기억 추가
                agent.add_memory(f"당신이 {target_name}에게 말했습니다: \"{message}\"") # 자신도 기억
            else:
                agent.add_memory(f"{target_name}에게 말하려고 했지만, 찾을 수 없었습니다.")
        
        elif say_match: # 공개 대화
            message = say_match.group(1).strip()
            observation = f"{agent.name}이(가) 말합니다: \"{message}\""
            self.broadcast_observation(agent, observation, public=True)
        
        elif assign_match:
            target_name, task = assign_match.group(1).strip(), assign_match.group(2).strip()
            if target_name in self.agents:
                target_agent = self.agents[target_name]
                target_agent.assign_task(task)
                observation = f"{agent.name}이(가) {target_name}에게 '{task}' 작업을 할당했습니다."
                self.broadcast_observation(agent, observation, public=True)
            else:
                agent.add_memory(f"{target_name}에게 작업을 할당하려 했지만, 찾을 수 없었습니다.")

        # ... (DO, REPORT, FIX 등 다른 행동 처리)
        else:
            # 공개적으로 영향을 미치는 다른 행동들
            public_action = False
            if do_match:
                observation = f"{agent.name}이(가) {do_match.group(1).strip()}."
                public_action = True # DO 행동은 주변에서 볼 수 있음
            elif report_match:
                feature, issue = report_match.group(1).strip(), report_match.group(2).strip()
                if feature in self.project_status:
                    self.project_status[feature] = f"버그 발생 ({issue})"
                    observation = f"{agent.name}이(가) 프로젝트 보드에 '{feature}'의 버그를 보고했습니다: {issue}"
                    public_action = True
            elif fix_match:
                feature = fix_match.group(1).strip()
                if feature in self.project_status:
                    self.project_status[feature] = "정상"
                    observation = f"{agent.name}이(가) '{feature}'의 버그를 수정하고 프로젝트 보드를 업데이트했습니다."
                    public_action = True
            
            if public_action:
                self.broadcast_observation(agent, observation, public=True)
            elif not observation: # 매치되는 행동이 없을 경우
                observation = f"{agent.name}이(가) 알 수 없는 행동('{action_string}')을 시도합니다."
                agent.add_memory(observation)

    def broadcast_observation(self, acting_agent, observation, public=False):
        """행동의 결과를 다른 에이전트에게 전달합니다."""
        # 공개(public) 행동은 같은 장소에 있는 모두가 관찰
        if public:
            for agent in self.agents.values():
                if agent.location == acting_agent.location:
                    agent.add_memory(observation)
        # 비공개 행동은 행동 주체만 기억 (이미 add_memory 호출됨)

class Agent:
    """자율적으로 행동하는 에이전트. 작업 목록 기능이 추가되었습니다."""
    def __init__(self, name, description, llm_client, memory_db):
        self.name = name
        self.description = description
        self.llm_client = llm_client
        self.memory_db = memory_db
        self.location = None
        self.task_list = [] # 작업 목록 추가
        self.reflection_threshold = 50
        self.recent_importance_sum = 0
        self.recent_memories_for_reflection = []
        print(f"'{self.name}' 에이전트(4단계 기능 탑재)가 생성되었습니다.")
    
    def assign_task(self, task):
        """외부에서 작업을 할당받습니다."""
        self.task_list.append(task)
        self.add_memory(f"새로운 작업이 할당되었습니다: {task}")

    # add_memory, _calculate_importance, reflect, perceive 메소드는 이전과 동일
    def add_memory(self, observation):
        importance_score = self._calculate_importance(observation)
        timestamp = datetime.datetime.now()
        metadata = {"timestamp": timestamp.isoformat(), "type": "observation", "importance": importance_score}
        self.memory_db.add_memory(observation, metadata)
        print(f"[{self.name}의 기억 추가 (중요도: {importance_score})] {observation}")
        self.recent_importance_sum += importance_score
        self.recent_memories_for_reflection.append(observation)
        if self.recent_importance_sum >= self.reflection_threshold: self.reflect()
    def _calculate_importance(self, memory_text):
        prompt = f"당신은 AI 에이전트의 사고 과정을 보조하는 분석 시스템입니다.\n다음 문장이 에이전트의 장기적인 목표나 행동에 얼마나 중요한지 1(일상적)에서 10(매우 중요) 사이의 정수로 평가해주세요.\n오직 숫자만 응답하세요.\n\n문장: \"{memory_text}\"\n중요도:"
        response = self.llm_client.generate_response(prompt)
        try: return int(response)
        except (ValueError, TypeError): return 3
    def reflect(self):
        print(f"\n--- [{self.name}의 성찰 시작] (누적 중요도: {self.recent_importance_sum}) ---")
        memories_str = "\n".join(self.recent_memories_for_reflection)
        prompt = f"당신은 '{self.name}' AI 에이전트입니다.\n다음은 당신의 최근 경험들입니다:\n{memories_str}\n\n이 경험들을 바탕으로 얻을 수 있는 3가지 중요한 결론이나 통찰을 요약해주세요.\n이 통찰은 당신의 미래 행동에 지침이 될 것입니다."
        reflection_text = self.llm_client.generate_response(prompt)
        metadata = {"timestamp": datetime.datetime.now().isoformat(), "type": "reflection", "importance": 10}
        self.memory_db.add_memory(f"성찰: {reflection_text}", metadata)
        print(f"[{self.name}의 성찰 완료] {reflection_text}")
        self.recent_importance_sum = 0
        self.recent_memories_for_reflection = []
        print("--- 성찰 종료 ---\n")
    def perceive(self, world):
        if not self.location: return
        location_state = world.get_location_state(self.location)
        self.add_memory(location_state)

    def plan_and_act(self, world):
        """작업 목록과 직접 대화까지 고려하여 행동을 결정합니다."""
        if not self.llm_client: return "DO: 가만히 있는다."
        
        current_situation = f"현재 위치: {self.location}. {world.get_location_state(self.location)}"
        retrieved_memories = self.memory_db.retrieve_memories(current_situation, n_results=5)
        memories_str = "\n".join(retrieved_memories)
        
        # 작업 목록을 프롬프트에 추가
        tasks_str = "\n- ".join(self.task_list) if self.task_list else "없음"
        
        # 현재 위치에 있는 다른 에이전트 목록
        other_agents = [name for name in world.locations.get(self.location, []) if name != self.name]
        other_agents_str = ", ".join(other_agents) if other_agents else "없음"

        prompt = f"""
당신은 '{self.name}'이며, '{self.description}' 역할을 수행하는 AI 에이전트입니다.
현재 상황: {current_situation}

당신의 현재 작업 목록:
- {tasks_str}

최근 기억 및 관련 정보:
{memories_str}

이 모든 정보를 종합하여, 당신의 역할과 현재 작업 목록에 가장 부합하는 단일 행동을 결정해주세요.
**작업 목록에 있는 일을 우선적으로 처리해야 합니다.**

선택 가능한 행동 형식 (대화 가능한 대상: {other_agents_str}):
- MOVE to [장소]
- SAY: [공개 메시지]
- SAY to [대상]: [개인 메시지]
- DO: [행동 서술]
- REPORT BUG: [기능] is [문제점]
- FIX BUG: [기능]
- ASSIGN TASK to [대상]: [작업 내용] (당신이 PM일 경우)

오직 행동 문자열 하나만 응답하세요.
"""
        action = self.llm_client.generate_response(prompt)
        
        # 작업이 완료되었는지 확인 (간단한 키워드 기반)
        if self.task_list and ("FIX BUG" in action or "완료" in action or "수정" in action):
            completed_task = self.task_list.pop(0)
            self.add_memory(f"작업 완료: {completed_task}")

        return action
